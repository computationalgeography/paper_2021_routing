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
    array_shape = flow_direction.shape

    return flow_direction


def perform_calculations(
        flow_direction):

    partition_id = None # TODO lfr.partition_id(flow_direction)
    inflow_count = lfr.inflow_count(flow_direction)
    stream_class = lfr.accu_info3(flow_direction)

    return partition_id, inflow_count, stream_class


def write_outputs(
        flow_direction,
        partition_id,
        inflow_count,
        stream_class,
        input_dataset_pathname,
        array_pathname,
        output_dataset_pathname):

    phenomenon_name, property_set_name, _ = array_pathname.split("/")

    input_dataset = ldm.open_dataset(input_dataset_pathname, "r")
    space_box = lstdm.space_box(input_dataset, phenomenon_name, property_set_name)

    io_tuples = [
            (flow_direction, "flow_direction"),
            # TODO (partition_id, "partition_id"),
            (inflow_count, "inflow_count"),
            (stream_class, "stream_class"),
        ]
    lstfr.write_rasters(
        output_dataset_pathname, phenomenon_name, property_set_name, flow_direction.shape, space_box, io_tuples)


@lstfr.lue_init
def accu_info3():

    input_dataset_pathname, array_pathname, output_dataset_pathname = parse_command_line()

    # TODO
    partition_shape = (1700, 1700)
    # partition_shape = (500, 500)
    flow_direction = create_inputs(input_dataset_pathname, array_pathname, partition_shape)

    partition_id, inflow_count, stream_class = perform_calculations(flow_direction)

    write_outputs(
        flow_direction, partition_id, inflow_count, stream_class,
        input_dataset_pathname, array_pathname, output_dataset_pathname)


accu_info3()
