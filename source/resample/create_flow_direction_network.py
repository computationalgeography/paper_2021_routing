import os.path
import sys
sys.path = [
    os.path.join(os.path.split(__file__)[0], "..")
] + sys.path

import lue.data_model as ldm
import lue.framework as lfr
import lue_staging.data_model as lstdm
import lue_staging.framework as lstfr
import numpy as np
import docopt


@lstfr.lue_init
def create_flow_direction_network():

    usage = """\
Usage:
    {command} <input_dataset> <elevation> <output_dataset>
""".format(
        command=os.path.basename(sys.argv[0]))

    argv = [arg for arg in sys.argv[1:] if not arg.startswith("--hpx")]
    arguments = docopt.docopt(usage, argv)
    input_dataset_pathname = arguments["<input_dataset>"]
    elevation_pathname = arguments["<elevation>"]
    output_dataset_pathname = arguments["<output_dataset>"]


    # Read elevation and calculate flow direction
    partition_shape = (2000, 2000)
    elevation = lfr.read_array("{}/{}".format(input_dataset_pathname, elevation_pathname), partition_shape)
    array_shape = elevation.shape

    flow_direction = lfr.d8_flow_direction(elevation)


    # Write dataset
    phenomenon_name, property_set_name, _ = elevation_pathname.split("/")
    input_dataset = ldm.open_dataset(input_dataset_pathname, "r")
    space_box = lstdm.space_box(input_dataset, phenomenon_name, property_set_name)
    del input_dataset

    io_tuples = [
            (elevation, "elevation"),
            (flow_direction, "flow_direction"),
        ]
    lstfr.write_rasters(
        output_dataset_pathname, phenomenon_name, property_set_name, array_shape, space_box, io_tuples)

    ### del elevation


    ### # Verify flow_direction network is OK by calling accu threshold
    ### material = lfr.create_array(array_shape, partition_shape, np.dtype(np.float32), 1.0)
    ### threshold = lfr.create_array(array_shape, partition_shape, np.dtype(np.float32), 10.0)
    ### outflow, remainder = lfr.accu_threshold3(flow_direction, material, threshold)


if __name__ == "__main__":
    create_flow_direction_network()
