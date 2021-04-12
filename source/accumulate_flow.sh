#!/usr/bin/env bash
set -e

lue_translate="$LUE_OBJECTS/bin/lue_translate"

input_dataset_pathname="/mnt/data1/home/kor/data/project/routing/dem_ldd/108680/ldd_108680.lue"
flow_direction_array_pathname="area/raster/ldd_108680"

# input_dataset_pathname="/mnt/data1/home/kor/data/project/routing/africa/africa.lue"
# flow_direction_array_pathname="area/raster/flow_direction"

# input_dataset_pathname="/mnt/data1/home/kor/data/project/routing/africa2/ldd_africa.lue"
# flow_direction_array_pathname="area/raster/ldd"

# input_dataset_pathname="/mnt/data1/home/kor/data/project/routing/dem_ldd/ldd_southafrica/south_africa.lue"
# flow_direction_array_pathname="area/raster/ldd_southafrica"

output_prefix="/tmp"
output_dataset_pathname="$output_prefix/tmp.lue"


# NOTE: using multiple localities requires a build of LUE with support for
#     parallel I/O
nr_localities=1
nr_threads_per_locality=4

PYTHONPATH=$LUE/../paper_2021_routing/source/:$PYTHONPATH \
    `which python` $LUE_OBJECTS/_deps/hpx-build/bin/hpxrun.py \
        --localities=$nr_localities \
        --thread=$nr_threads_per_locality \
        --parcelport=tcp \
        --verbose \
        `which python` -- $LUE/../paper_2021_routing/source/accumulate_flow.py \
            $input_dataset_pathname $flow_direction_array_pathname \
            $output_dataset_pathname


# Post-processing
layer_names="
    flow_direction
    inflow_count
    inter_partition_stream
    flow_accumulation
    flow_accumulation_fraction_flux
    flow_accumulation_fraction_state
"

for layer_name in $layer_names;
do
    $lue_translate export -m $output_prefix/$layer_name.json \
        $output_dataset_pathname $output_prefix/$layer_name.tif
done
