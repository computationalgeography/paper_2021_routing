import lue.data_model as ldm
import lue.framework as lfr
import lue_staging as lst
import docopt
import os.path
import sys


@lst.lue_init
@lst.duration
def accumulate_flow():

    usage = """\
Accumulate flow

Usage:
    {command} <input_dataset> <flow_direction> <output_dataset>
""".format(
        command=os.path.basename(sys.argv[0]))

    arguments = docopt.docopt(usage)
    input_dataset_pathname = arguments["<input_dataset>"]
    array_pathname = arguments["<flow_direction>"]
    output_dataset_pathname = arguments["<output_dataset>"]
    partition_shape = (1000, 1000)

    phenomenon_name, property_set_name, flow_direction_layer_name = array_pathname.split("/")

    # Read flow directions from existing LUE dataset into array
    array_pathname = \
        os.path.join(input_dataset_pathname, phenomenon_name, property_set_name, flow_direction_layer_name)
    flow_direction = lfr.read_array(array_pathname, partition_shape)
    array_shape = flow_direction.shape

    # Perform calculations on flow direction network
    inflow_count = lfr.inflow_count(flow_direction)

    material = lfr.create_array(array_shape, partition_shape, lst.material_t, 1.0)
    flow_accumulation = lfr.accu(flow_direction, material)

    fraction = lfr.create_array(array_shape, partition_shape, lst.fraction_t, 0.5)
    flow_accumulation_fraction_flux, flow_accumulation_fraction_state = \
        lfr.accu_fraction(flow_direction, material, fraction)

    # Write results to dataset
    input_dataset = ldm.open_dataset(input_dataset_pathname)
    space_box = lst.space_box(input_dataset, phenomenon_name, property_set_name)
    output_dataset = ldm.create_dataset(output_dataset_pathname)

    io_tuples = [
            (flow_direction, "flow_direction"),
            (inflow_count, "inflow_count"),
            (flow_accumulation, "flow_accumulation"),
            (flow_accumulation_fraction_flux, "flow_accumulation_fraction_flux"),
            (flow_accumulation_fraction_state, "flow_accumulation_fraction_state"),
        ]

    write_fs = lst.write_rasters(
        output_dataset, phenomenon_name, property_set_name, array_shape, space_box, io_tuples)

    # Wait for the writes (and the preceding calculations) to have
    # finished. Otherwise the timings will only be measuring the creation
    # of the tasks, instead of also the execution.
    lst.wait_all(write_fs)


accumulate_flow()
