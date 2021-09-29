import os.path
import sys
sys.path = [
    os.path.join(os.path.split(__file__)[0], "..", "..", "lue/benchmark/lue")
] + sys.path
import benchmark
import benchmark.cluster
import fiona
from osgeo import gdal
import math

gdal.UseExceptions()


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

    # High overhead means lots of resources are occupied with other stuff. The amount of memory
    # available is (1 - overhead_fraction) * total memory.
    overhead_fraction = {
            "eejit": 0.2,
            "gransasso": 0.3,
        }
    cluster_partition_size = {
            "eejit": 4,
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
        platform,
        overhead_fraction):

    # Memory provided for each platform is in GiB, which is 1024**3 bytes, not GB, which is
    # 1000**3 bytes.
    # Calculate the number of cells that fit in the memory available per core. Using more cells
    # will require more memory, increasing the chance that memory from other NUMA nodes will be
    # used, for example. That will make the benchmark results harder to interpret.
    nr_bytes_available_per_core = \
        (platform.cluster.cluster_node.memory * 1024**3) / platform.cluster.cluster_node.nr_cores
    max_nr_cells_possible_per_core = nr_bytes_available_per_core / nr_bytes_needed_per_cell

    # This is a maximum. Tweak its value if necessary, using the overhead_fraction.
    # In practice, less memory is available than calculated above. Other processes and the
    # runtime system and task tree also take up some memory. How much depends on the platform
    # and the experiment.
    nr_cells_per_core = (1.0 - overhead_fraction) * max_nr_cells_possible_per_core

    # Calculate possible array sizes by multiplying the nr_cells_per_core by the number of
    # cores per NUMA node, cluster node, and cluster partition.
    nr_cores_per_numa_node = platform.cluster.cluster_node.package.numa_node.nr_cores
    nr_numa_nodes_per_cluster_node = platform.cluster.cluster_node.nr_numa_nodes
    nr_cluster_nodes_per_cluster_partition = platform.cluster_partition_size

    nr_bytes_available_per_numa_node = nr_bytes_available_per_core * nr_cores_per_numa_node
    nr_bytes_available_per_cluster_node = nr_bytes_available_per_numa_node * nr_numa_nodes_per_cluster_node

    nr_cells_per_numa_node = nr_cores_per_numa_node * nr_cells_per_core
    nr_cells_per_cluster_node = nr_numa_nodes_per_cluster_node * nr_cells_per_numa_node
    nr_cells_per_cluster_partition = nr_cluster_nodes_per_cluster_partition * nr_cells_per_cluster_node

    array_size_per_core = array_size(nr_cells_per_core)
    array_size_per_numa_node = array_size(nr_cells_per_numa_node)
    array_size_per_cluster_node = array_size(nr_cells_per_cluster_node)
    array_size_per_cluster_partition = array_size(nr_cells_per_cluster_partition)

    # partition shape scaling experiment:
    # Use amount of memory that fits in the hardware occupied by the max number of workers. The
    # partition size found works well for the total hardware size. Partition sizes found when
    # using smaller problems and less hardware are not that different.
    # - cores: array_size_per_numa_node
    # - numa nodes: array_size_per_cluster_node
    # - cluster_node: array_size_per_cluster_partition

    # strong scaling experiment:
    # Use amount of memory that fits in the hardware occupied by a single worker. Otherwise
    # the single worker will potentially perform less well because remote memory is being used,
    # and scaling efficiencies will be over-estimated.
    # - cores: array_size_per_core
    # - numa node: array_size_per_numa_node
    # - cluster node: array_size_per_cluster_node
    # Rationale: Process a certain amount of work faster by adding more hardware. Therefore,
    # the amount of work must fit in the memory occupied by a single worker.

    # weak scaling experiment:
    # Use amount of memory that fits in the hardware occupied by a single worker. It is OK to
    # use a smaller problem in case the experiments take longer than needed. Never use a larger
    # problem.
    # - cores: array_size_per_core
    # - numa node: array_size_per_numa_node
    # - cluster node: array_size_per_cluster_node

    memory_sizes = {
            "core": nr_bytes_available_per_core / 1024**3,
            "numa_node": nr_bytes_available_per_numa_node / 1024**3,
            "cluster_node": nr_bytes_available_per_cluster_node / 1024**3,
        }

    # If these sizes are too large, then increase the overhead fraction.
    # If these sizes are too low, then decrease the overhead fraction.
    # Note that the amount of memory used by the task tree on the root node is not included in
    # these calculations. The size of the task tree depends on the experiment. Use the sizes
    # as hints. Never use larger arrays than printed here. That would imply a bug in the
    # calculations or overhead_fraction.
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

    return memory_sizes, array_shapes


def raster_information(
        dataset_name):

    raster = gdal.Open(dataset_name)

    # Origin is north-west corner of raster
    x_origin, cell_width, _, y_origin, _, cell_height = raster.GetGeoTransform()

    assert cell_width == abs(cell_height)
    cell_size = cell_width

    crs = raster.GetProjectionRef()
    nr_rows = raster.RasterYSize
    nr_cols = raster.RasterXSize

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
