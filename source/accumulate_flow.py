import lue.data_model as ldm
import lue.framework as lfr
import lue_staging.data_model as lstdm
import lue_staging.framework as lstfr
import lue_staging as lst
import docopt
import os.path
import sys


def parse_command_line():
    usage = """\
Accumulate flow

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
    lstfr.wait_all([
        lfr.maximum(flow_direction),
        lfr.maximum(material),
        lfr.maximum(fraction)])

    return flow_direction, material, fraction


@lst.duration("perform_calculations")
def perform_calculations(
        flow_direction,
        material,
        fraction):

    inflow_count = lfr.inflow_count(flow_direction)
    inter_partition_stream = lfr.inter_partition_stream(flow_direction)

    flow_accumulation = lfr.accu(flow_direction, material)

    flow_accumulation_fraction_flux, flow_accumulation_fraction_state = \
        lfr.accu_fraction(flow_direction, material, fraction)

    # Blocks
    lstfr.wait_all([
        lfr.maximum(inflow_count),
        lfr.maximum(inter_partition_stream),
        lfr.maximum(flow_accumulation),
        lfr.maximum(flow_accumulation_fraction_flux),
        lfr.maximum(flow_accumulation_fraction_state)])

    return inflow_count, inter_partition_stream, flow_accumulation, flow_accumulation_fraction_flux, flow_accumulation_fraction_state


@lst.duration("write_outputs")
def write_outputs(
        flow_direction,
        inflow_count,
        inter_partition_stream,
        flow_accumulation,
        flow_accumulation_fraction_flux,
        flow_accumulation_fraction_state,
        input_dataset_pathname,
        array_pathname,
        output_dataset_pathname):

    phenomenon_name, property_set_name, _ = array_pathname.split("/")

    input_dataset = ldm.open_dataset(input_dataset_pathname, "r")
    space_box = lstdm.space_box(input_dataset, phenomenon_name, property_set_name)

    io_tuples = [
            (flow_direction, "flow_direction"),
            (inflow_count, "inflow_count"),
            (inter_partition_stream, "inter_partition_stream"),
            (flow_accumulation, "flow_accumulation"),
            (flow_accumulation_fraction_flux, "flow_accumulation_fraction_flux"),
            (flow_accumulation_fraction_state, "flow_accumulation_fraction_state"),
        ]

    # Blocks
    lstfr.write_rasters(
        output_dataset_pathname, phenomenon_name, property_set_name, flow_direction.shape, space_box, io_tuples)


@lstfr.lue_init
@lst.duration("overall")
def accumulate_flow():

    # Initialize (blocks)
    input_dataset_pathname, array_pathname, output_dataset_pathname = parse_command_line()
    partition_shape = (1000, 1000)
    flow_direction, material, fraction = create_inputs(input_dataset_pathname, array_pathname, partition_shape)

    # Calculate (blocks)
    inflow_count, inter_partition_stream, \
    flow_accumulation, flow_accumulation_fraction_flux, flow_accumulation_fraction_state = \
        perform_calculations(flow_direction, material, fraction)

    # Write outputs (blocks)
    write_outputs(
        flow_direction, inflow_count, inter_partition_stream,
        flow_accumulation, flow_accumulation_fraction_flux, flow_accumulation_fraction_state,
        input_dataset_pathname, array_pathname, output_dataset_pathname)


accumulate_flow()
