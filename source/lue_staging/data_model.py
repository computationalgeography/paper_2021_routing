import json
import os.path


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
