import docopt
from osgeo import gdal
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.patches as mpatches
import numpy as np
import glob
import math
import os.path
import sys


usage = """\
Create plots, videos, etc of accu_info results

Usage:
    {command} <prefix>
""".format(
    command = os.path.basename(sys.argv[0]))


ready = 31
hot = 32
cold = 33

# partition_classes = [hot, cold, ready]
partition_classes = [ready, hot, cold]

class_colours = {
        ready: "#a3be8c",
        hot: "#bf616a",
        cold: "#5e81ac",
    }
heatmap_colours = [
        "#2e3440",
        "#3b4252",
        "#bf616a",
        "#d08770",
        "#ebcb8b",
        "#e5e9f0",
    ]
range_colours = heatmap_colours
labels = {
        ready: "ready",
        hot: "hot",
        cold: "cold",
    }


def plot_inflow_count_raster(
        array,
        plot_pathname):

    colour_map = colors.ListedColormap(range_colours)
    nr_classes = len(range_colours)

    min = 0.0
    max = 8.0
    class_width = (max - min) / nr_classes
    min -= 0.01 * class_width

    bins = [min + (i * class_width) for i in range(nr_classes + 1)]
    norm = matplotlib.colors.BoundaryNorm(bins, nr_classes)

    figure, axes = plt.subplots()
    image = axes.imshow(array, cmap=colour_map, norm=norm)

    plt.axis("off")
    plt.savefig("{}.png".format(plot_pathname), bbox_inches="tight")
    plt.savefig("{}.pdf".format(plot_pathname), bbox_inches="tight")
    plt.close()


def plot_partition_class_raster(
        array,
        plot_pathname):

    colour_map = colors.ListedColormap(
        [class_colours[partition_class] for partition_class in sorted(partition_classes)])

    bins = np.sort(partition_classes) + 0.5
    bins = np.insert(bins, 0, np.min(bins) - 1.0)
    norm = matplotlib.colors.BoundaryNorm(bins, len(partition_classes))

    figure, axes = plt.subplots()
    image = axes.imshow(array, cmap=colour_map, norm=norm)

    patches = [
            mpatches.Patch(color=class_colours[partition_class], label=labels[partition_class])
                for partition_class in partition_classes
        ]
    axes.legend(handles=patches, loc="lower right")

    plt.axis("off")
    plt.savefig("{}.png".format(plot_pathname), bbox_inches="tight")
    plt.savefig("{}.pdf".format(plot_pathname), bbox_inches="tight")
    plt.close()


def plot_solvable_fraction_raster(
        array,
        plot_pathname):

    colour_map = colors.ListedColormap(range_colours)
    nr_classes = len(range_colours)

    min = 0.0
    max = 1.0
    class_width = (max - min) / nr_classes
    min -= 0.01 * class_width

    bins = [min + (i * class_width) for i in range(nr_classes + 1)]
    norm = matplotlib.colors.BoundaryNorm(bins, nr_classes)

    figure, axes = plt.subplots()
    image = axes.imshow(array, cmap=colour_map, norm=norm)

    plt.axis("off")
    plt.savefig("{}.png".format(plot_pathname), bbox_inches="tight")
    plt.savefig("{}.pdf".format(plot_pathname), bbox_inches="tight")
    plt.close()


def plot_nr_cells_to_solve_raster(
        array,
        plot_pathname):

    colour_map = colors.ListedColormap(range_colours)
    nr_classes = len(range_colours)

    min = np.min(array)
    max = 5  # np.max(array)
    class_width = (max - min) / nr_classes
    min -= 0.01 * class_width

    bins = [min + (i * class_width) for i in range(nr_classes + 1)]
    norm = matplotlib.colors.BoundaryNorm(bins, nr_classes)

    figure, axes = plt.subplots()
    image = axes.imshow(array, cmap=colour_map, norm=norm)

    plt.axis("off")
    plt.savefig("{}.png".format(plot_pathname), bbox_inches="tight")
    plt.savefig("{}.pdf".format(plot_pathname), bbox_inches="tight")
    plt.close()


def plot_heatmap(
        array,
        plot_pathname):

    colour_map = colors.ListedColormap(heatmap_colours)
    nr_classes = len(heatmap_colours)

    min = np.min(array)
    max = np.max(array)
    class_width = (max - min) / len(heatmap_colours)
    min -= 0.5 * class_width

    bins = [min + (i * class_width) for i in range(len(heatmap_colours) + 1)]
    norm = matplotlib.colors.BoundaryNorm(bins, len(heatmap_colours))

    figure, axes = plt.subplots()
    image = axes.imshow(array, cmap=colour_map, norm=norm)

    plt.axis("off")
    plt.savefig("{}.png".format(plot_pathname), bbox_inches="tight")
    plt.savefig("{}.pdf".format(plot_pathname), bbox_inches="tight")
    plt.close()


def iteration_number(
        pathname):

    # Get rid of the directory name
    basename = os.path.split(pathname)[1]

    # Get rid of the extension
    basename = os.path.splitext(basename)[0]

    # Get rid of the part before the number
    number = basename.split("-")[1]

    return int(number)


def create_video(
        png_pathnames,
        animation_pathname):

    # TODO https://matplotlib.org/stable/gallery/animation/dynamic_image.html#sphx-glr-gallery-animation-dynamic-image-py

    assert len(png_pathnames) > 0

    png_root_name, png_basename = os.path.split(png_pathnames[0])
    png_basename, png_ext = os.path.splitext(png_basename)
    png_basename = png_basename.split("-")[0]
    png_pattern = os.path.join(png_root_name, "{}-%d{}".format(png_basename, png_ext))

    command = \
        "ffmpeg -y -loglevel warning -framerate 2 -i {} -s:v 1280x720 -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p {}" \
        .format(png_pattern, animation_pathname)
    os.system(command)


def plot_partition_class_counts(
        iterations,
        counts,
        plot_pathname):

    colour_map = colors.ListedColormap(
        [class_colours[partition_class] for partition_class in partition_classes])

    figure, axes = plt.subplots()

    axes.stackplot(iterations,
            *[counts[partition_class] for partition_class in partition_classes],
            colors=[class_colours[partition_class] for partition_class in partition_classes],
            labels=[labels[partition_class] for partition_class in partition_classes])
    axes.legend(loc="lower right")

    plt.savefig("{}.png".format(plot_pathname), bbox_inches="tight")
    plt.savefig("{}.pdf".format(plot_pathname), bbox_inches="tight")
    plt.close()


    # Push each iteration back, depending on the number of hot
    # partitions. This gives an impression of the relative importance of
    # the hot partitions.
    iterations[0] = 0
    for i in range(len(iterations) - 1):
        iterations[i + 1] = iterations[i] + counts[hot][i]

    figure, axes = plt.subplots()

    axes.stackplot(iterations,
            *[counts[partition_class] for partition_class in partition_classes],
            colors=[class_colours[partition_class] for partition_class in partition_classes],
            labels=[labels[partition_class] for partition_class in partition_classes])
    axes.legend(loc="lower right")

    plt.savefig("{}-scaled.png".format(plot_pathname), bbox_inches="tight")
    plt.savefig("{}-scaled.pdf".format(plot_pathname), bbox_inches="tight")
    plt.close()


def post_process_inflow_count(
        raster_pathname):

    plot_pathname = os.path.splitext(raster_pathname)[0]

    raster = gdal.Open(raster_pathname)
    band = raster.GetRasterBand(1)
    array = band.ReadAsArray()

    plot_inflow_count_raster(array, plot_pathname)


def post_process_partition_class(
        raster_pathname,
        animation_pathname):

    # The raster pathname passed in is a glob pattern we can use to
    # detect which rasters to use for the animation

    # Determine which raster to use for the animation
    raster_pathnames = glob.glob(raster_pathname)
    raster_pathnames.sort()

    # Style the rasters
    png_pathnames = []
    iterations = []
    counts = {}
    heatmap = None
    cutoff = None

    for raster_pathname in raster_pathnames:
        plot_pathname = os.path.splitext(raster_pathname)[0]

        raster = gdal.Open(raster_pathname)
        band = raster.GetRasterBand(1)
        array = band.ReadAsArray()

        i = iteration_number(raster_pathname)

        (unique, counts_) = np.unique(array, return_counts=True)

        for partition_class in [ready, hot, cold]:
            if not partition_class in unique:
                unique = np.append(unique, partition_class)
                counts_ = np.append(counts_, 0)

        if i == 0:
            cutoff = counts_[unique == ready]

        counts_i = zip(unique, counts_)

        for value, count in counts_i:
            counts.setdefault(value, []).append(count)

        iterations.append(i)

        if heatmap is None:
            heatmap = np.zeros_like(array)

        heatmap += array == hot

        plot_partition_class_raster(array, plot_pathname)
        png_pathnames.append("{}.png".format(plot_pathname))

    create_video(png_pathnames, animation_pathname)

    output_prefix = os.path.split(animation_pathname)[0]
    plot_pathname = os.path.join(output_prefix, "partition_class_counts")

    sort_idxs = np.argsort(iterations)
    iterations = np.array(iterations)[sort_idxs]
    for partition_class in counts:
        counts[partition_class] = np.array(counts[partition_class])[sort_idxs]

    nr_partitions = math.prod(array.shape)
    print(nr_partitions)
    print("nr hot partitions:")
    print("  maximum: {}".format(nr_partitions * len(iterations)))
    print("  actual : {}".format(np.sum(counts[hot])))

    # Get rid of the partitions that are already ready. These likely
    # only contain no-data cells.
    counts[ready] -= cutoff

    plot_partition_class_counts(
        iterations, counts, os.path.join(output_prefix, "partition_class_counts"))
    plot_heatmap(heatmap, os.path.join(output_prefix, "heatmap"))


def post_process_solvable_fraction(
        raster_pathname,
        animation_pathname):

    # The raster pathname passed in is a glob pattern we can use to
    # detect which rasters to use for the animation

    # Determine which raster to use for the animation
    raster_pathnames = glob.glob(raster_pathname)
    raster_pathnames.sort()

    # Style the rasters
    png_pathnames = []

    for raster_pathname in raster_pathnames:
        plot_pathname = os.path.splitext(raster_pathname)[0]

        raster = gdal.Open(raster_pathname)
        band = raster.GetRasterBand(1)
        array = band.ReadAsArray()

        plot_solvable_fraction_raster(array, plot_pathname)
        png_pathnames.append("{}.png".format(plot_pathname))


    create_video(png_pathnames, animation_pathname)


def post_process_nr_cells_to_solve(
        raster_pathname,
        animation_pathname):

    raster_pathnames = glob.glob(raster_pathname)
    raster_pathnames.sort()

    png_pathnames = []

    for raster_pathname in raster_pathnames:
        plot_pathname = os.path.splitext(raster_pathname)[0]

        raster = gdal.Open(raster_pathname)
        band = raster.GetRasterBand(1)
        array = band.ReadAsArray()

        plot_nr_cells_to_solve_raster(array, plot_pathname)
        png_pathnames.append("{}.png".format(plot_pathname))


    create_video(png_pathnames, animation_pathname)


def post_process(
        prefix):

    # In the prefix we expect to find
    # - partition_class-*.tif
    # - solvable_fraction-*.tif

    post_process_inflow_count(
        os.path.join(prefix, "inflow_count.tif"))
    post_process_partition_class(
        os.path.join(prefix, "partition_class-*.tif"),
        os.path.join(prefix, "partition_class.mp4"))
    post_process_solvable_fraction(
        os.path.join(prefix, "solvable_fraction-*.tif"),
        os.path.join(prefix, "solvable_fraction.mp4"))
    post_process_nr_cells_to_solve(
        os.path.join(prefix, "nr_cells_to_solve-*.tif"),
        os.path.join(prefix, "nr_cells_to_solve.mp4"))


if __name__ == "__main__":
    arguments = docopt.docopt(usage)

    prefix = arguments["<prefix>"]

    post_process(prefix)
