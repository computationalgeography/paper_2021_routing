#!/usr/bin/env python
"""
Given some properties of a platform and a benchmark, calculate array sizes to use for various
scaling experiments.
"""
import os.path
import sys
import docopt
from util import *
import pprint


usage = """\
Usage:
    {command} <platform> <overhead_fraction> <nr_bytes_initial> <nr_bytes_simulate> <nr_steps_in_flight>
        [<raster> <x_center> <y_center> <vector>]

Options:
    platform            Name of the platform
    overhead_fraction   Fraction of memory taken by runtime, task tree, ...
    tree_size           Nr of bytes used by the task tree
    nr_bytes_initial    Nr of bytes used per cell for initial model state
    nr_bytes_simulate   Nr of bytes used per cell per time step
    nr_steps_in_flight  Max nr of time steps for which tasks are created
    raster              ...
    x_center            ...
    y_center            ...
    vector              ...

Number of bytes needed per cell is calculated as:
    nr_bytes_initial + (nr_steps_in_flight * nr_bytes_simulate)
""".format(
        command=os.path.basename(sys.argv[0]))


if __name__ == "__main__":
    arguments = docopt.docopt(usage)
    platform_name = arguments["<platform>"]
    overhead_fraction = float(arguments["<overhead_fraction>"])

    nr_bytes_initial_state = int(arguments["<nr_bytes_initial>"])
    nr_bytes_per_timestep = int(arguments["<nr_bytes_simulate>"])
    nr_timesteps_in_flight = int(arguments["<nr_steps_in_flight>"])

    nr_bytes_needed_per_cell = nr_bytes_initial_state + (nr_timesteps_in_flight * nr_bytes_per_timestep)
    assert nr_bytes_needed_per_cell > 0


    # Determine array shapes for various kinds of scaling experiments
    # flow accumulation benchmark:
    #     flow_direction (uint8) + material + threshold + result (all float32)
    #     nr_bytes_needed_per_cell = 1 + 4 + 4 + 4
    #     nr_bytes_needed_per_cell += 2  # inflow_count + copy
    # case-study-model:
    #         flow_direction (uint8) + material + threshold + outflow + remainder (all float32)
    #     nr_bytes_needed_per_cell = 1 + (4 * 4) => 17
    #         inflow_count + copy
    #         nr_bytes_needed_per_cell += 2 => 19
    #         multiple time_steps = 3 => 57


    memory_sizes, array_shapes = \
        calculate_array_shapes(nr_bytes_needed_per_cell, platform(platform_name), overhead_fraction)

    for worker in ["core", "numa_node", "cluster_node"]:
        if worker in array_shapes:
            print(80 * "-")
            print(worker)
            print("→ max memory / worker: {} GiB".format(memory_sizes[worker]))
            pprint.pprint(array_shapes[worker], indent=4)
    print(80 * "-")
    print("WARNING: these are maximum sizes! Do not use larger sizes.")

    # Determine center of arrays and write bounding boxes of arrays
    if not arguments["<raster>"] is None:
        raster_dataset_name = arguments["<raster>"]
        center = (float(arguments["<x_center>"]), float(arguments["<y_center>"]))
        vector_dataset_name = arguments["<vector>"]

        (crs, origin, cell_size, dimensions) = raster_information(raster_dataset_name)
        array_center = calculate_array_center(origin, center, cell_size)
        print("Cell indices of array center: {}".format(array_center))

        write_array_bounding_boxes(crs, origin, cell_size, dimensions, array_center, array_shapes, vector_dataset_name)
