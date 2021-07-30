import lue.data_model as ldm
import lue.framework as lfr
import lue_staging.data_model as lstdm
from collections.abc import Iterable
import os.path


def lue_init(user_main):

    def decorated_function(*args, **kwargs):

        hpx_configuration = [
            # Make sure hpx_main is always executed
            "hpx.run_hpx_main!=1",
            # Allow for unknown command line options
            "hpx.commandline.allow_unknown!=1",
            # Disable HPX' short options
            "hpx.commandline.aliasing!=0",
            # Don't print diagnostics during forced terminate
            "hpx.diagnostics_on_terminate!=0",
            # Make AGAS clean up resources faster than by default
            "hpx.agas.max_pending_refcnt_requests!=50",

            # Got an HPX error when processing Africa dataset:
            #     mmap() failed to allocate thread stack due to
            #     insufficient resources, increase
            #     /proc/sys/vm/max_map_count or add
            #     -Ihpx.stacks.use_guard_pages=0 to the command line
            "hpx.stacks.use_guard_pages!=0",
        ]

        # for key in os.environ:
        #     if key.startswith("SLURM"):
        #         print("{}: {}".format(key, os.environ[key]))

        lfr.start_hpx_runtime(hpx_configuration)

        if lfr.on_root_locality():
            user_main(*args, **kwargs)

        # lfr.stop_hpx_runtime()

    return decorated_function


def write_rasters(
        dataset_pathname,
        phenomenon_name,
        property_set_name,
        array_shape,
        space_box,
        io_tuples):

    dataset = ldm.create_dataset(dataset_pathname)

    raster_view = ldm.hl.create_raster_view(
        dataset, phenomenon_name, property_set_name, array_shape, space_box)

    for io_tuple in io_tuples:
        array, layer_name = io_tuple

        if isinstance(array, Iterable):
            for i in range(len(array)):
                layer_name_i = "{}-{}".format(layer_name, i)
                raster_view.add_layer(layer_name_i, array[i].dtype)
        else:
            raster_view.add_layer(layer_name, array.dtype)

    # Let go of the dataset. Otherwise the next writes will fail.
    del raster_view
    del dataset

    for io_tuple in io_tuples:
        array, layer_name = io_tuple
        property_set_pathname = os.path.join(dataset_pathname, phenomenon_name, property_set_name)

        if isinstance(array, Iterable):
            for i in range(len(array)):
                layer_name_i = "{}-{}".format(layer_name, i)
                array_pathname = os.path.join(property_set_pathname, layer_name_i)

                lfr.write_array(array[i], array_pathname)

                lstdm.write_translate_json(dataset_pathname, phenomenon_name, property_set_name, layer_name_i)
        else:
            array_pathname = os.path.join(property_set_pathname, layer_name)

            lfr.write_array(array, array_pathname)

            lstdm.write_translate_json(dataset_pathname, phenomenon_name, property_set_name, layer_name)


def write_rasters2(
        dataset_pathname,
        raster_view,
        phenomenon_name,
        property_set_name,
        io_tuples):

    for io_tuple in io_tuples:
        array, layer_name = io_tuple

        if isinstance(array, Iterable):
            for i in range(len(array)):
                layer_name_i = "{}-{}".format(layer_name, i)
                raster_view.add_layer(layer_name_i, array[i].dtype)
        else:
            raster_view.add_layer(layer_name, array.dtype)

    # Let go of the dataset. Otherwise the next writes will fail.
    del raster_view
    # del dataset

    for io_tuple in io_tuples:
        array, layer_name = io_tuple
        property_set_pathname = os.path.join(dataset_pathname, phenomenon_name, property_set_name)

        if isinstance(array, Iterable):
            for i in range(len(array)):
                layer_name_i = "{}-{}".format(layer_name, i)
                array_pathname = os.path.join(property_set_pathname, layer_name_i)

                lfr.write_array(array[i], array_pathname)

                lstdm.write_translate_json(dataset_pathname, phenomenon_name, property_set_name, layer_name_i)
        else:
            array_pathname = os.path.join(property_set_pathname, layer_name)

            lfr.write_array(array, array_pathname)

            lstdm.write_translate_json(dataset_pathname, phenomenon_name, property_set_name, layer_name)


def wait_all(
        futures):
    """
    Wait for all futures to be ready

    This blocks the current thread!

    The result is discarded.
    """
    for future in futures:
        if hasattr(future, "get"):
            future.get()
        else:
            lfr.wait(future)


def add_raster_layers(
        raster_view,
        io_tuples):

    for io_tuple in io_tuples:
        array, layer_name = io_tuple

        if isinstance(array, Iterable):
            for i in range(len(array)):
                layer_name_i = "{}-{}".format(layer_name, i)
                raster_view.add_layer(layer_name_i, array[i].dtype)
        else:
            raster_view.add_layer(layer_name, array.dtype)


def write_rasters3(
        dataset_pathname,
        phenomenon_name,
        property_set_name,
        io_tuples):

    for io_tuple in io_tuples:
        array, layer_name = io_tuple
        property_set_pathname = os.path.join(dataset_pathname, phenomenon_name, property_set_name)

        if isinstance(array, Iterable):
            for i in range(len(array)):
                layer_name_i = "{}-{}".format(layer_name, i)
                array_pathname = os.path.join(property_set_pathname, layer_name_i)

                lfr.write_array(array[i], array_pathname)

                lstdm.write_translate_json(dataset_pathname, phenomenon_name, property_set_name, layer_name_i)
        else:
            array_pathname = os.path.join(property_set_pathname, layer_name)

            print("write {}/{}...".format(dataset_pathname, array_pathname))
            lfr.write_array(array, array_pathname)

            lstdm.write_translate_json(dataset_pathname, phenomenon_name, property_set_name, layer_name)
