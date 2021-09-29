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
import pprint
import timeit


def parse_command_line():
    usage = """\
Usage:
    {command} <input_dataset> <flow_direction> <center> <shape>
""".format(
        command=os.path.basename(sys.argv[0]))

    argv = [arg for arg in sys.argv[1:] if not arg.startswith("--hpx")]
    arguments = docopt.docopt(usage, argv)
    input_dataset_pathname = arguments["<input_dataset>"]
    array_pathname = arguments["<flow_direction>"]
    subset_center= tuple(map(int, arguments["<center>"].split(",")))
    subset_shape= tuple(map(int, arguments["<shape>"].split(",")))

    assert(len(subset_center) == len(subset_shape) == 2)

    return input_dataset_pathname, array_pathname, subset_center, subset_shape


def create_inputs(
        dataset_pathname,
        array_pathname,
        subset_center,
        subset_shape,
        partition_shape):

    flow_direction = lfr.read_array(
        "{}/{}".format(dataset_pathname, array_pathname), subset_center, subset_shape, partition_shape)

    return flow_direction


def run_model(
        flow_direction,
        partition_shape,
        count,
        dependent,
        synchronize):

    material = lfr.create_array(flow_direction.shape, partition_shape, np.dtype(np.float32), 5.0)
    threshold = lfr.create_array(flow_direction.shape, partition_shape, np.dtype(np.float32), 5.0)
    lstfr.wait_all([flow_direction, material, threshold])

    durations = []

    for c in range(count):
        start_time = timeit.default_timer()

        outflow, residue = lfr.accu_threshold3(flow_direction, material, threshold)
        if synchronize: lstfr.wait_all([outflow, residue])

        if dependent:
            dummy, _ = lfr.accu_threshold3(flow_direction, outflow, threshold)
        else:
            dummy, _ = lfr.accu_threshold3(flow_direction, material, threshold)

        lstfr.wait_all([outflow, residue, dummy])
        durations.append(timeit.default_timer() - start_time)

    return Result(partition_shape, synchronize, min(durations))


@lstfr.lue_init
def composability():

    input_dataset_pathname, array_pathname, subset_center, subset_shape = parse_command_line()

    count = 1
    partition_shapes = [(2500, 2500)]

    synchronization_label = {
            True: "synchronous",
            False: "asynchronous",
        }
    dependency_label = {
            True: "dependent",
            False: "independent",
        }
    results_pickle_pathname = {}
    results = {}

    for dependent in [True, False]:
        results_pickle_pathname[dependent] = "composability-{}.p".format(dependency_label[dependent])
        results[dependent] = []

    # NOTE Update when caching is needed again
    # if os.path.exists(results_pickle_pathname[dependent]):
    #     results[dependent] = pickle.load(open(results_pickle_pathname[dependent], "rb"))

    for partition_shape in partition_shapes:

        flow_direction = create_inputs(
            input_dataset_pathname, array_pathname, subset_center, subset_shape, partition_shape)

        for dependent in [True, False]:

            for synchronize in [True, False]:

                experiment_already_performed = any([result for result in results[dependent] if
                    result.partition_shape == partition_shape and result.synchronize == synchronize])

                print("{} / {} / {} ...".format(
                    partition_shape, dependency_label[dependent], synchronization_label[synchronize]))

                if experiment_already_performed:
                    print("... cached")
                else:
                    results[dependent].append(run_model(flow_direction, partition_shape, count,
                        dependent=dependent, synchronize=synchronize))
                    print("... done")


    for dependent in [True, False]:
        print(dependency_label[dependent])
        pprint.pprint(results[dependent])
        pickle.dump(results[dependent], open(results_pickle_pathname[dependent], "wb"))


composability()
