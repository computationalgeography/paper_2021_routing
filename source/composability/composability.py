import os.path
import sys
sys.path = [
    os.path.join(os.path.split(__file__)[0], "..")
] + sys.path

from result import Result
import lue.framework as lfr
import lue_staging.framework as lstfr
import docopt
import numpy as np
import pickle
import timeit


def parse_command_line():
    usage = """\
Usage:
    {command} <input_dataset> <flow_direction>
""".format(
        command=os.path.basename(sys.argv[0]))

    argv = [arg for arg in sys.argv[1:] if not arg.startswith("--hpx")]
    arguments = docopt.docopt(usage, argv)
    input_dataset_pathname = arguments["<input_dataset>"]
    array_pathname = arguments["<flow_direction>"]

    return input_dataset_pathname, array_pathname


def create_inputs(
        dataset_pathname,
        array_pathname,
        partition_shape):

    flow_direction = lfr.read_array("{}/{}".format(dataset_pathname, array_pathname), partition_shape)

    return flow_direction


def run_model(
        flow_direction,
        partition_shape,
        synchronize):

    # Run a 'model' and keep track of the time it takes

    # Preparation
    precipitation = lfr.create_array(flow_direction.shape, partition_shape, np.dtype(np.float32), 1.0)
    infiltration_capacity = lfr.create_array(flow_direction.shape, partition_shape, np.dtype(np.float32), 20.0)
    almost_one = lfr.uniform(precipitation, -0.95, 1.05)
    lstfr.wait_all([precipitation, infiltration_capacity, almost_one])
    nr_time_steps = 2

    # Statements to measure
    start_time = timeit.default_timer()

    for t in range(nr_time_steps):

        precipitation *= almost_one
        if synchronize:
            lstfr.wait_all([precipitation])

        infiltration_capacity *= almost_one
        if synchronize:
            lstfr.wait_all([infiltration_capacity])

        runoff, infiltration = lfr.accu_threshold3(flow_direction, precipitation, infiltration_capacity)
        if synchronize:
            lstfr.wait_all([runoff, infiltration])

        runoff *= almost_one
        if synchronize:
            lstfr.wait_all([runoff])

        infiltration_capacity *= almost_one
        if synchronize:
            lstfr.wait_all([infiltration_capacity])

    lstfr.wait_all([runoff])

    elapsed = timeit.default_timer() - start_time

    return Result(partition_shape, synchronize, elapsed)


@lstfr.lue_init
def composability():

    input_dataset_pathname, array_pathname = parse_command_line()

    results_pickle_pathname = "composability.p"

    if os.path.exists(results_pickle_pathname):
        results = pickle.load(open(results_pickle_pathname, "rb"))
    else:
        results = []

    for partition_shape in [
            (500, 500), (1000, 1000), (2000, 2000), (3000, 3000), (4000, 4000), (5000, 5000),
            (6000, 6000), (7000, 7000), (8000, 8000), (9000, 9000), (10000, 10000)]:
        flow_direction = create_inputs(input_dataset_pathname, array_pathname, partition_shape)

        for synchronize in [False, True]:
            experiment_already_performed = any([result for result in results if
                result.partition_shape == partition_shape and result.synchronize == synchronize])

            print("{} / {} ...".format(partition_shape, synchronize))
            if experiment_already_performed:
                print("... cached")
            else:
                results.append(run_model(flow_direction, partition_shape, synchronize=synchronize))
                print("... done")

    pickle.dump(results, open(results_pickle_pathname, "wb"))


composability()
