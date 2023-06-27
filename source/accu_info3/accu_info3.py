import os.path
import sys
sys.path = [
    os.path.join(os.path.split(__file__)[0], "..")
] + sys.path

import lue.data_model as ldm
import lue.framework as lfr
import lue_staging.data_model as lstdm
import lue_staging.framework as lstfr
import docopt
import numpy as np


def parse_command_line():
    usage = """\
Usage:
    {command} <input_dataset> <flow_direction> <output_dataset>
""".format(
        command=os.path.basename(sys.argv[0]))

    argv = [arg for arg in sys.argv[1:] if not arg.startswith("--hpx")]
    arguments = docopt.docopt(usage, argv)
    input_dataset_pathname = arguments["<input_dataset>"]
    array_pathname = arguments["<flow_direction>"]
    output_dataset_pathname = arguments["<output_dataset>"]

    return input_dataset_pathname, array_pathname, output_dataset_pathname


def create_inputs(
        dataset_pathname,
        array_pathname,
        partition_shape):

    flow_direction = lfr.read_array("{}/{}".format(dataset_pathname, array_pathname), partition_shape)

    return flow_direction


def perform_calculations(
        flow_direction,
        partition_shape):

    # Try to get good timestamps, not influenced by other work, and cast to element type that
    # is supported by GDAL
    material = lfr.create_array(flow_direction.shape, partition_shape, np.dtype(np.float32), 1.0)
    lfr.wait(material)
    flow_accumulation = lfr.accu3(flow_direction, material)
    timestamp = lfr.timestamp(flow_accumulation)
    lfr.wait(timestamp)
    timestamp -= lfr.minimum(timestamp)
    timestamp = lfr.cast(timestamp, np.dtype(np.float32))
    del material

    locality_id = lfr.locality_id(flow_direction)
    partition_id = lfr.array_partition_id(flow_direction)
    inflow_count = lfr.inflow_count(flow_direction)
    stream_class = lfr.accu_info3(flow_direction)

    return locality_id, partition_id, flow_accumulation, inflow_count, stream_class, timestamp


def write_outputs(
        flow_direction,
        locality_id,
        partition_id,
        flow_accumulation,
        inflow_count,
        stream_class,
        timestamp,
        input_dataset_pathname,
        array_pathname,
        output_dataset_pathname):

    phenomenon_name, property_set_name1, _ = array_pathname.split("/")

    input_dataset = ldm.open_dataset(input_dataset_pathname, "r")
    space_box = lstdm.space_box(input_dataset, phenomenon_name, property_set_name1)

    output_dataset = ldm.create_dataset(output_dataset_pathname)

    io_tuples1 = [
            (partition_id, "partition_id"),
            (flow_direction, "flow_direction"),
            (flow_accumulation, "flow_accumulation"),
            (inflow_count, "inflow_count"),
            (stream_class, "stream_class"),
        ]

    raster_view = ldm.hl.create_raster_view(
        output_dataset, phenomenon_name, property_set_name1, flow_direction.shape, space_box)
    lstfr.add_raster_layers(raster_view, io_tuples1)

    property_set_name2 = "partition"
    io_tuples2 = [
            (locality_id, "locality_id"),
            (timestamp, "timestamp"),
        ]
    raster_view = ldm.hl.create_raster_view(
        output_dataset, phenomenon_name, property_set_name2, flow_direction.shape_in_partitions, space_box)
    lstfr.add_raster_layers(raster_view, io_tuples2)

    # Release the dataset, otherwise the next writes will fail
    del raster_view
    del output_dataset

    lstfr.write_rasters3(output_dataset_pathname, phenomenon_name, property_set_name1, io_tuples1)
    lstfr.write_rasters3(output_dataset_pathname, phenomenon_name, property_set_name2, io_tuples2)


@lstfr.lue_init
def accu_info3():

    input_dataset_pathname, array_pathname, output_dataset_pathname = parse_command_line()

    # partition_shape = (2000, 2000)
    # partition_shape = (1000, 1000)
    partition_shape = (750, 750)
    # partition_shape = (500, 500)
    flow_direction = create_inputs(input_dataset_pathname, array_pathname, partition_shape)

    locality_id, partition_id, flow_accumulation, inflow_count, stream_class, timestamp = \
        perform_calculations(flow_direction, partition_shape)

    write_outputs(
        flow_direction, locality_id, partition_id, flow_accumulation, inflow_count, stream_class, timestamp,
        input_dataset_pathname, array_pathname, output_dataset_pathname)


accu_info3()
