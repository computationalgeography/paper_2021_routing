#!/usr/bin/env bash
set -e

lue_translate="$LUE_OBJECTS/bin/lue_translate"

input_dataset_pathname="/mnt/data1/home/kor/data/project/routing/dem_ldd/108680/ldd_108680.lue"
flow_direction_array_pathname="area/raster/ldd_108680"

# input_dataset_pathname="/mnt/data1/home/kor/data/project/routing/africa/africa.lue"
# flow_direction_array_pathname="area/raster/flow_direction"

output_prefix="/tmp"
output_dataset_pathname="$output_prefix/tmp.lue"

PYTHONPATH=$LUE/../paper_2021_routing/source/:$PYTHONPATH \
    python $LUE/accumulate_flow.py \
        $input_dataset_pathname $flow_direction_array_pathname \
        $output_dataset_pathname

layer_names="
    flow_direction
    inflow_count
    flow_accumulation
    flow_accumulation_fraction_flux
    flow_accumulation_fraction_state
"

for layer_name in $layer_names;
do
    $lue_translate export -m $output_prefix/$layer_name.json \
        $output_dataset_pathname $output_prefix/$layer_name.tif
done
