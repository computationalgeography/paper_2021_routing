"""
This script executes a flow accumulation operation and an operation
before and after it. Depending on the load-imbalance in the flow
accumulation operation, tasks from the operation after the flow
accumulation operation will start executing. This can be visualized
in Vampir.
"""
import lue.data_model as ldm
import lue.framework as lfr
import lue_staging as lst
import docopt
import os.path
import sys


def parse_command_line():
    usage = """\
Accumulate flow

Usage:
    {command} <input_dataset> <flow_direction>
""".format(
        command=os.path.basename(sys.argv[0]))

    argv = [arg for arg in sys.argv[1:] if not arg.startswith("--hpx")]
    arguments = docopt.docopt(usage, argv)
    input_dataset_pathname = arguments["<input_dataset>"]
    array_pathname = arguments["<flow_direction>"]

    return input_dataset_pathname, array_pathname


@lst.duration("create_inputs")
def create_inputs(
        dataset_pathname,
        array_pathname,
        partition_shape):

    flow_direction = lfr.read_array("{}/{}".format(dataset_pathname, array_pathname), partition_shape)
    array_shape = flow_direction.shape
    material = lfr.create_array(array_shape, partition_shape, lst.material_t, 1.0)
    fraction = lfr.create_array(array_shape, partition_shape, lst.fraction_t, 0.75)

    # Blocks
    lst.wait_all([
        lfr.maximum(flow_direction),
        lfr.maximum(material),
        lfr.maximum(fraction)])

    return flow_direction, material, fraction


@lst.duration("perform_calculations")
def perform_calculations(
        flow_direction,
        material,
        fraction):

    # Continue until the Vampir trace makes sense
    # - A too long task is 20s
    # - A good task is 100 microseconds - few milliseconds
    #     [100 μs - ms]
    #     [100.000 ns - 1.000.000 ns]

    inflow_count = lfr.inflow_count(flow_direction)
    inter_partition_stream = lfr.inter_partition_stream(flow_direction)
    flow_accumulation = lfr.accu(flow_direction, material)
    flow_accumulation_fraction_flux, flow_accumulation_fraction_state = \
        lfr.accu_fraction(flow_direction, material, fraction)

    # Blocks
    lst.wait_all([
            lfr.maximum(inflow_count),
            lfr.maximum(inter_partition_stream),
            lfr.maximum(flow_accumulation),
            lfr.maximum(flow_accumulation_fraction_flux),
            lfr.maximum(flow_accumulation_fraction_state),
        ])


@lst.lue_init
@lst.duration("overall")
def accumulate_flow():

    # Initialize (blocks)
    input_dataset_pathname, array_pathname = parse_command_line()
    partition_shape = (1000, 1000)
    flow_direction, material, fraction = create_inputs(input_dataset_pathname, array_pathname, partition_shape)

    # Calculate (blocks)
    perform_calculations(flow_direction, material, fraction)

accumulate_flow()
