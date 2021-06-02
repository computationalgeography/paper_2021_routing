import os.path
import sys
sys.path=[
        os.path.join(os.environ["LUE"], "benchmark", "lue")
    ] + sys.path
import benchmark
import benchmark.cluster
import fiona
import math


class Platform(object):

    def __init__(self,
            name,
            cluster_settings_json,
            cluster_partition_size,
            overhead_fraction):

        self.name = name

        # Hardware
        self.cluster = benchmark.cluster.Cluster(cluster_settings_json)
        self.cluster_partition_size = cluster_partition_size

        # overhead_fraction of memory is used by non-data (OS, runtime, tmp data structures, ...)
        assert 0 <= overhead_fraction <= 1, overhead_fraction
        self.overhead_fraction = overhead_fraction


def platform(
        platform_name):

    overhead_fraction = {
            "eejit": 0.4,
            "gransasso": 0.7,
        }
    cluster_partition_size = {
            "eejit": 6,
            "gransasso": 1,
            "snowdon": 1,
        }

    platform = Platform(
        name=platform_name,
        cluster_settings_json=benchmark.json_to_data(
            os.path.join(os.environ["LUE"], "benchmark", "configuration", platform_name, "cluster.json")),
        cluster_partition_size=cluster_partition_size[platform_name],
        overhead_fraction=overhead_fraction[platform_name])

    return platform


def calculate_array_center(
        origin,
        center,
        cell_size):

    x_origin, y_origin = origin
    x_center, y_center = center

    row_center = (y_origin - y_center) / cell_size
    col_center = (x_center - x_origin) / cell_size

    return (row_center, col_center)


def array_size(
        count):
    array_size = math.sqrt(count)
    array_size = round(array_size, -3)
    return int(array_size)


def calculate_array_shapes(
        nr_bytes_needed_per_cell,
        platform):

    nr_bytes_available_per_core = \
            platform.cluster.cluster_node.memory * 1024**3 / platform.cluster.cluster_node.nr_cores
    max_nr_cells_possible_per_core = nr_bytes_available_per_core / nr_bytes_needed_per_cell

    # This is a maximum. Tweak its value if necessary (using the overhead_fraction).
    nr_cells_per_core = (1.0 - platform.overhead_fraction) * max_nr_cells_possible_per_core

    nr_cores_per_numa_node = platform.cluster.cluster_node.package.numa_node.nr_cores
    nr_numa_nodes_per_cluster_node = platform.cluster.cluster_node.nr_numa_nodes
    nr_cluster_nodes_per_cluster_partition = platform.cluster_partition_size

    nr_cells_per_numa_node = nr_cores_per_numa_node * nr_cells_per_core
    nr_cells_per_cluster_node = nr_numa_nodes_per_cluster_node * nr_cells_per_numa_node
    nr_cells_per_cluster_partition = nr_cluster_nodes_per_cluster_partition * nr_cells_per_cluster_node

    array_size_per_core = array_size(nr_cells_per_core)
    array_size_per_numa_node = array_size(nr_cells_per_numa_node)
    array_size_per_cluster_node = array_size(nr_cells_per_cluster_node)
    array_size_per_cluster_partition = array_size(nr_cells_per_cluster_partition)

    # partition shape scaling experiment:
    # - Use amount of memory that fits in the hardware occupied by the max number of workers
    #    - cores: array_size_per_numa_node
    #    - numa nodes: array_size_per_cluster_node
    #    - cluster_node: array_size_per_cluster_partition_n

    # strong scaling experiment:
    # - Use amount of memory that fits in the hardware occupied by a single worker:
    #     - cores: array_size_per_core
    #     - numa node: array_size_per_numa_node
    #     - cluster node: array_size_per_cluster_node

    # weak scaling experiment:
    # - Use amount of memory that fits in the hardware occupied by a single worker:
    #     - cores: array_size_per_core
    #     - numa node: array_size_per_numa_node
    #     - cluster node: array_size_per_cluster_node

    array_shapes = {
            "core": {
                    "max_nr_workers": nr_cores_per_numa_node,
                    "partition_shape": 2 * (array_size_per_numa_node,),
                    "strong_scaling": 2 * (array_size_per_core,),
                    "weak_scaling": 2 * (array_size_per_core,),
                }
        }

    if nr_numa_nodes_per_cluster_node > 1:
        array_shapes["numa_node"] = {
                "max_nr_workers": nr_numa_nodes_per_cluster_node,
                "partition_shape": 2 * (array_size_per_cluster_node,),
                "strong_scaling": 2 * (array_size_per_numa_node,),
                "weak_scaling": 2 * (array_size_per_numa_node,),
            }

    if nr_cluster_nodes_per_cluster_partition > 1:
        array_shapes["cluster_node"] = {
                "max_nr_workers": nr_cluster_nodes_per_cluster_partition,
                "partition_shape": 2 * (array_size_per_cluster_partition,),
                "strong_scaling": 2 * (array_size_per_cluster_node,),
                "weak_scaling": 2 * (array_size_per_cluster_node,),
            }

    return array_shapes


def raster_information(
        dataset_name):

    # TODO Read all this from the dataset

    crs = "EPSG:4326 - WGS 84 - Geographic"

    # Degrees, north-west corner of raster
    x_origin = -18.0
    y_origin = 38.0
    cell_size = 0.0008333333333333333868

    nr_rows = 87600
    nr_cols = 84000

    return crs, (x_origin, y_origin), cell_size, (nr_rows, nr_cols)


def write_array_bounding_boxes(
        crs,
        origin,
        cell_size,
        dimensions,
        center,
        array_shapes,
        vector_dataset_name):
    """
    Write a shape file containing the bounding box passed in
    """
    metadata = {
            "driver": "ESRI Shapefile",
            "schema": {
                    "geometry": "Polygon",
                    "properties": {
                            "kind": "str",  # Kind of worker: core, numa node, cluster node
                            "nr_workers": "int:32",
                            "nr_cells": "int:32",
                        }
                },
            "crs": crs,
        }

    # Create new dataset
    with fiona.open(vector_dataset_name, "w", **metadata) as dataset:

        # For each kind of worker ...
        for worker in ["core", "numa_node", "cluster_node"]:

            kind = worker

            if worker in array_shapes:

                max_nr_workers = array_shapes[worker]["max_nr_workers"]
                array_shape = array_shapes[worker]["weak_scaling"]
                assert array_shape[0] == array_shape[1]
                array_size = math.prod(array_shape)

                # ... and for each nr_workers ...

                for nr_workers in range(1, max_nr_workers + 1):

                    # ... write a bounding box and the kind, nr_workers attribute values
                    array_size_worker = nr_workers * array_size
                    array_shape_worker = 2 * (math.sqrt(array_size_worker),)
                    # print(kind, nr_workers, array_shape_worker)

                    north = origin[1] - (center[0] - math.floor(0.5 * array_shape_worker[0])) * cell_size
                    south = origin[1] - (center[0] + math.ceil(0.5 * array_shape_worker[0])) * cell_size
                    west = origin[0] + (center[1] - math.floor(0.5 * array_shape_worker[1])) * cell_size
                    east = origin[0] + (center[1] + math.ceil(0.5 * array_shape_worker[1])) * cell_size

                    assert abs(((north - south) / cell_size) - array_shape_worker[0]) < 1.0
                    assert abs(((east - west) / cell_size) - array_shape_worker[1]) < 1.0

                    geometry = {
                            # Order coordinates counter-clockwise, facing "up"
                            "coordinates": [[
                                (west, north),
                                (west, south),
                                (east, south),
                                (east, north),
                                (west, north),
                            ]],
                            "type": "Polygon",
                        }
                    properties = {
                            "kind": kind,
                            "nr_workers": nr_workers,
                            "nr_cells": array_size_worker,
                        }
                    dataset.write({"geometry": geometry, "properties": properties})
