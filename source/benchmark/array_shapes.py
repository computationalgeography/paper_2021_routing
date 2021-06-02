#!/usr/bin/env python
import os.path
import sys
import docopt
from util import *
import pprint


usage = """\
Usage:
    {command} <platform> <raster> <x_center> <y_center> <vector>
""".format(
        command=os.path.basename(sys.argv[0]))


if __name__ == "__main__":
    arguments = docopt.docopt(usage)
    platform_name = arguments["<platform>"]
    raster_dataset_name = arguments["<raster>"]
    center = (float(arguments["<x_center>"]), float(arguments["<y_center>"]))
    vector_dataset_name = arguments["<vector>"]

    # Determine array shapes for various kinds of scaling experiments
    # flow accumulation benchmark:
    #     flow_direction (uint8) + material + threshold + result (all float32)
    nr_bytes_needed_per_cell = 1 + 4 + 4 + 4
    array_shapes = calculate_array_shapes(nr_bytes_needed_per_cell, platform(platform_name))

    pprint.pprint(array_shapes)

    # Determine center of arrays and write bounding boxes of arrays
    (crs, origin, cell_size, dimensions) = raster_information(raster_dataset_name)
    array_center = calculate_array_center(origin, center, cell_size)
    print("Cell indices of array center: {}".format(array_center))

    write_array_bounding_boxes(crs, origin, cell_size, dimensions, array_center, array_shapes, vector_dataset_name)
