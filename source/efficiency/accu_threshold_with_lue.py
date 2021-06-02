"""
Calculate accu_threshold with LUE and report the amount of time
it took.
"""
import lue.data_model as ldm
import lue.framework as lfr
import lue_staging as lst
import lue_staging.data_model as lstdm
import lue_staging.framework as lstfr
import docopt
import os.path
import sys


def parse_command_line():
    usage = """\
Accu threshold

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
    material = lfr.create_array(array_shape, partition_shape, lst.material_t, 10.0)
    threshold = lfr.create_array(array_shape, partition_shape, lst.threshold_t, 5.0)

    # Blocks
    lstfr.wait_all([
        lfr.maximum(flow_direction),
        lfr.maximum(material),
        lfr.maximum(threshold)])

    return flow_direction, material, threshold


@lst.duration("perform_calculations")
def perform_calculations(
        flow_direction,
        material,
        threshold):

    flux, state = lfr.accu_threshold(flow_direction, material, threshold)

    # Blocks
    lstfr.wait_all([
        lfr.maximum(flux),
        lfr.maximum(state)])

    return flux


@lst.duration("write_outputs")
def write_outputs(
        flow_direction,
        flux,
        input_dataset_pathname,
        array_pathname,
        output_dataset_pathname):

    phenomenon_name, property_set_name, _ = array_pathname.split("/")

    input_dataset = ldm.open_dataset(input_dataset_pathname, "r")
    space_box = lstdm.space_box(input_dataset, phenomenon_name, property_set_name)

    io_tuples = [
            (flow_direction, "flow_direction"),
            (flux, "flux"),
        ]

    # Blocks
    lstfr.write_rasters(
        output_dataset_pathname, phenomenon_name, property_set_name, flow_direction.shape, space_box, io_tuples)


@lstfr.lue_init
@lst.duration("overall")
def accumulate_flow():

    # Initialize (blocks)
    input_dataset_pathname, array_pathname, output_dataset_pathname = parse_command_line()
    partition_shape = (1700, 1700)
    flow_direction, material, threshold = create_inputs(input_dataset_pathname, array_pathname, partition_shape)

    # Calculate (blocks)
    flux = perform_calculations(flow_direction, material, threshold)

    # Write outputs (blocks)
    write_outputs(flow_direction, flux, input_dataset_pathname, array_pathname, output_dataset_pathname)


accumulate_flow()
