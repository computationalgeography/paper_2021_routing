from result import Result
import matplotlib.pyplot as plt
import numpy as np
import pickle
import pprint


def postprocess(
        results,
        plot_pathame):

    # Results contains records for the experiments performed. Each experiment varies these aspects:
    # - partition_shape
    # - asynchronous / synchronous
    #
    # Each experiment resulted in a duration (seconds) executing the model took.
    #
    # Create a plot that shows how duration varies per experiment:
    # - Bargraph with per partition_shape / synchronize combination the duration

    labels = [str(result.partition_shape) for result in results if not result.synchronize]
    asynchronous_durations = [result.duration for result in results if not result.synchronize]
    synchronous_durations = [result.duration for result in results if result.synchronize]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width / 2, synchronous_durations, width, label="Synchronous")
    rects2 = ax.bar(x + width / 2, asynchronous_durations, width, label="Asynchronous")

    ax.set_ylabel("Duration (s)")
    ax.set_title("Synchronous and asynchronous durations by partition shape")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Partition shape")
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    fig.tight_layout()
    plt.savefig("{}.png".format(plot_pathname), bbox_inches="tight")
    plt.savefig("{}.pdf".format(plot_pathname), bbox_inches="tight")


plot_pathname = "duration"
results = pickle.load(open("composability.p", "rb"))
pprint.pprint(results)
postprocess(results, plot_pathname)
