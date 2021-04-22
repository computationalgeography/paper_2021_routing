# Stuff that might end up in the LUE code
import lue.data_model as ldm
import lue.framework as lfr
import numpy as np
import json
import timeit
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


# 1: east,                6
# 2: southeast,           3
# 4: south,               2
# 8: southwest,           1
# 16: west,               4
# 32: northwest,          7
# 64: north.              8
# 128: northeast          9
# 0: river mouth,         5
# -1: inland depression,  wtf?
# -9: undefined (ocean)   255

# Africa dataset:
# 247: no-data
# 0: no-data


nominal_t = np.dtype(np.uint32)
flow_direction_t = np.dtype(np.uint8)
material_t = np.dtype(np.float32)
fraction_t = np.dtype(np.float32)


# def reclassify_flow_direction(
#         flow_direction):
# 
#     flow_direction = lfr.where(flow_direction == 1, 6, flow_direction)
#     flow_direction = lfr.where(flow_direction == 2, 3, flow_direction)
#     flow_direction = lfr.where(flow_direction == 4, 2, flow_direction)
#     flow_direction = lfr.where(flow_direction == 8, 1, flow_direction)
#     flow_direction = lfr.where(flow_direction == 16, 4, flow_direction)
#     flow_direction = lfr.where(flow_direction == 32, 7, flow_direction)
#     flow_direction = lfr.where(flow_direction == 64, 8, flow_direction)
#     flow_direction = lfr.where(flow_direction == 128, 9, flow_direction)
# 
#     flow_direction = lfr.where(flow_direction == 0, 5, flow_direction)
# 
#     flow_direction = lfr.where(flow_direction == 247, 255, flow_direction)
# 
#     flow_direction = lfr.where(flow_direction == -1, 5, flow_direction)
#     flow_direction = lfr.where(flow_direction == -9, 255, flow_direction)
# 
#     # if flow_direction.dtype != flow_direction_t:
# 
#     # Reclassify flow directions to LUE conventions
#     # TODO
# 
#     return flow_direction


def space_box(
        dataset,
        phenomenon_name,
        property_set_name):

    # Lots of assumptions...
    return dataset.phenomena[phenomenon_name].property_sets[property_set_name].space_domain.value[0]


def write_translate_json(
        dataset_pathname,
        phenomenon_name,
        property_set_name,
        layer_name):
    """
    Create the file that lue_translate currently needs for exporting
    an array from a LUE dataset to a GDAL raster
    """
    dataset_directory_pathname, dataset_basename = os.path.split(dataset_pathname)

    object = {
        "{}".format(os.path.splitext(dataset_basename)[0]): {
            "phenomena": [
                {
                    "name": phenomenon_name,
                    "property_sets": [
                        {
                            "name": property_set_name,
                            "properties": [
                                {
                                    "name": layer_name,
                                }
                             ]
                        }
                    ]
                }
            ]
        }
    }

    meta_pathname = os.path.join(os.path.dirname(dataset_pathname), layer_name) + ".json"

    open(meta_pathname, "w").write(json.dumps(object, indent=4))


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
        property_set_pathname = os.path.join(dataset_pathname, phenomenon_name, property_set_name)

        raster_view.add_layer(layer_name, array.dtype)

    # Let go of the dataset. Otherwise the next writes will fail.
    del raster_view
    del dataset

    for io_tuple in io_tuples:
        array, layer_name = io_tuple
        property_set_pathname = os.path.join(dataset_pathname, phenomenon_name, property_set_name)
        array_pathname = os.path.join(property_set_pathname, layer_name)

        lfr.write_array(array, array_pathname)

        write_translate_json(dataset_pathname, phenomenon_name, property_set_name, layer_name)


def duration(label):
    def decorator(function):
        def decorated_function(*args, **kwargs):
            start_time = timeit.default_timer()
            result = function(*args, **kwargs)
            elapsed = timeit.default_timer() - start_time
            print("duration {}: {:.2}s / {:.2}m".format(label, elapsed, elapsed / 60))
            return result

        return decorated_function
    return decorator


def wait_all(
        futures):
    """
    Wait for all futures to be ready

    This blocks the current thread!

    The result is discarded.
    """
    for future in futures:
        future.get()
