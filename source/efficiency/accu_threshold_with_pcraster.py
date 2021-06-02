"""
Calculate accu_threshold with PCRaster and report the amount of time
it took.
"""
import lue_staging as lst
import pcraster
import docopt
import os.path
import sys


def parse_command_line():
    usage = """\
Accu threshold

Usage:
    {command} <flow_direction> <flux> <state>
""".format(
        command=os.path.basename(sys.argv[0]))

    arguments = docopt.docopt(usage)
    flow_direction_pathname = arguments["<flow_direction>"]
    flux_pathname = arguments["<flux>"]
    state_pathname = arguments["<state>"]

    return flow_direction_pathname, flux_pathname, state_pathname


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

    flux = pcraster.accuthresholdflux(flow_direction, material, threshold)

    return flux


@lst.duration("write_outputs")
def write_outputs(
        flux,
        flux_pathname):

    pcraster.report(flux, flux_pathname)


@lst.duration("overall")
def accumulate_flow():

    # Initialize
    flow_direction_pathname, flux_pathname, state_pathname = parse_command_line()
    flow_direction, material, threshold = create_inputs(flow_direction_pathname)

    # Calculate
    flux = perform_calculations(flow_direction, material, threshold)

    # Write outputs
    write_outputs(flux, flux_pathname)


accumulate_flow()
