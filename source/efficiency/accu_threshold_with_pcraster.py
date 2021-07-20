"""
Calculate accu_threshold with PCRaster and report the amount of time
it took.
"""
import os.path
import sys
sys.path = [
    os.path.join(os.path.split(__file__)[0], "..")
] + sys.path


import lue_staging as lst
import pcraster
import docopt


def parse_command_line():
    usage = """\
Accu threshold

Usage:
    {command} <flow_direction> <outflow>
""".format(
        command=os.path.basename(sys.argv[0]))

    arguments = docopt.docopt(usage)
    flow_direction_pathname = arguments["<flow_direction>"]
    outflow_pathname = arguments["<outflow>"]

    return flow_direction_pathname, outflow_pathname


@lst.duration("create_inputs")
def create_inputs(
        flow_direction_pathname):

    flow_direction = pcraster.readmap(flow_direction_pathname)
    material = pcraster.spatial(pcraster.scalar(10))
    threshold = pcraster.spatial(pcraster.scalar(5.0))

    return flow_direction, material, threshold


@lst.duration("perform_calculations")
def perform_calculations(
        flow_direction,
        material,
        threshold):

    outflow = pcraster.accuthresholdflux(flow_direction, material, threshold)

    return outflow


@lst.duration("write_outputs")
def write_outputs(
        outflow,
        outflow_pathname):

    pcraster.report(outflow, outflow_pathname)


@lst.duration("overall")
def accumulate_flow():

    # Initialize
    flow_direction_pathname, outflow_pathname = parse_command_line()
    flow_direction, material, threshold = create_inputs(flow_direction_pathname)

    # Calculate
    outflow = perform_calculations(flow_direction, material, threshold)

    # Write outputs
    write_outputs(outflow, outflow_pathname)


accumulate_flow()
