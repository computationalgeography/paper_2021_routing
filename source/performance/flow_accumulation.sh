#!/usr/bin/env bash
set -e

# Calculate flow accumulation using PCRaster and LUE. PCRaster uses a
# single core in the calculations. To be able to compare the results,
# the LUE version also uses a single core.

dirname="$( cd "$(dirname "$BASH_SOURCE")" ; pwd -P )"


# LUE:
# duration create_inputs: 1.6e+01s / 0.26m
# duration calculate_accu: 6.4e+01s / 1.1m
# duration calculate_accu_threshold: 8.2e+01s / 1.4m

# PCRaster:
# duration create_inputs: 1.3e+01s / 0.21m
# duration calculate_accu: 1.9e+02s / 3.2m
# duration calculate_accu_threshold: 2e+02s / 3.3m


function flow_accumulation_with_lue()
{
    output_prefix="$LUE_ROUTING_DATA/tmp"
    lue_translate="$LUE_OBJECTS/bin/lue_translate"

    export UCX_LOG_LEVEL=error

    area="south_africa"
    input_dataset_pathname="$LUE_ROUTING_DATA/$area/south_africa.lue"
    flow_direction_array_pathname="area/raster/ldd_southafrica"

    ### area="pyrenees"
    ### input_dataset_pathname="$LUE_ROUTING_DATA/$area/ldd_108680.lue"
    ### flow_direction_array_pathname="area/raster/ldd_108680"

    output_dataset_pathname="$output_prefix/$area.lue"

    export LD_PRELOAD=$GOOGLE_PERFTOOLS_ROOT/lib/libtcmalloc_minimal.so.4

    salloc \
        --ntasks=1 \
        --cpus-per-task=1 \
        mpirun \
            python \
                $dirname/flow_accumulation_with_lue.py \
                    $input_dataset_pathname $flow_direction_array_pathname \
                    $output_dataset_pathname \
                    --hpx:print-bind

    # layer_names="
    #     flow_direction
    #     outflow
    # "

    # for layer_name in $layer_names;
    # do
    #     $lue_translate export -m $output_prefix/$layer_name.json \
    #         $output_dataset_pathname $output_prefix/$layer_name.tif
    # done
}


function flow_accumulation_with_pcraster()
{
    PCRASTER=/scratch/depfg/pcraster/pcraster-4.3.1

    export PATH=$PCRASTER/bin:$PATH
    export PYTHONPATH=$PCRASTER/python:$PYTHONPATH


    routing_data_prefix="/scratch/depfg/jong0137/data/routing"
    data_prefix="$routing_data_prefix/south_africa"
    output_prefix="$routing_data_prefix/tmp"

    flow_direction_raster_pathname="$data_prefix/ldd_southafrica.map"
    flux_pathname="$output_prefix/outflow.map"

    salloc \
        --ntasks=1 \
        --cpus-per-task=1 \
        srun \
            python \
                $dirname/flow_accumulation_with_pcraster.py $flow_direction_raster_pathname $flux_pathname
}


flow_accumulation_with_lue
flow_accumulation_with_pcraster
