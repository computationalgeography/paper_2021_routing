#!/usr/bin/env bash
set -e

# Calculate accu_threshold using PCRaster and LUE. PCRaster uses a
# single core in the calculations. To be able to compare the results,
# the LUE version also uses a single core.

dirname="$( cd "$(dirname "$BASH_SOURCE")" ; pwd -P )"


function accu_threshold_with_lue()
{
    output_prefix="$LUE_ROUTING_DATA/tmp"
    lue_translate="$LUE_OBJECTS/bin/lue_translate"

    export UCX_LOG_LEVEL=error

    # ~44 GB
    # Old write:
    # duration create_inputs: 1.5e+01s / 0.25m
    # duration perform_calculations: 7.5e+01s / 1.2m
    # duration write_outputs: 1e+03s / 1.7e+01m
    # duration overall: 1.1e+03s / 1.9e+01m

    # New write:
    # duration create_inputs: 1.1e+01s / 0.19m
    # duration perform_calculations: 7.5e+01s / 1.2m
    # duration write_outputs: 2.3e+01s / 0.38m
    # duration overall: 1.1e+02s / 1.8m

    # accu_threshold3, and got rid of maximum() in favour of real wait():
    # duration create_inputs: 5.2s / 0.087m
    # duration perform_calculations: 7.9e+01s / 1.3m
    # duration write_outputs: 7.7s / 0.13m
    # duration overall: 9.2e+01s / 1.5m

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
                $dirname/accu_threshold_with_lue.py \
                    $input_dataset_pathname $flow_direction_array_pathname \
                    $output_dataset_pathname \
                    --hpx:print-bind

    layer_names="
        flow_direction
        outflow
    "

    for layer_name in $layer_names;
    do
        $lue_translate export -m $output_prefix/$layer_name.json \
            $output_dataset_pathname $output_prefix/$layer_name.tif
    done
}


function accu_threshold_with_pcraster()
{
    PCRASTER=/scratch/depfg/pcraster/pcraster-4.3.1

    export PATH=$PCRASTER/bin:$PATH
    export PYTHONPATH=$PCRASTER/python:$PYTHONPATH


    routing_data_prefix="/scratch/depfg/jong0137/data/routing"
    data_prefix="$routing_data_prefix/south_africa"
    output_prefix="$routing_data_prefix/tmp"

    # ~97 GB
    # PCRaster from conda-forge:
    # duration create_inputs: 4.0s / 0.067m
    # duration perform_calculations: 2.4e+02s / 4.1m
    # duration write_outputs: 1.5e+01s / 0.25m
    # duration overall: 2.6e+02s / 4.4m

    # Custom PCRaster on eejit:
    # duration create_inputs: 3.9s / 0.065m
    # duration perform_calculations: 1.9e+02s / 3.2m
    # duration write_outputs: 1.2e+01s / 0.2m
    # duration overall: 2.1e+02s / 3.5m

    # duration create_inputs: 4.7s / 0.078m
    # duration perform_calculations: 2.1e+02s / 3.5m
    # duration write_outputs: 9.8s / 0.16m
    # duration overall: 2.3e+02s / 3.8m

    flow_direction_raster_pathname="$data_prefix/ldd_southafrica.map"
    flux_pathname="$output_prefix/outflow.map"

    salloc \
        --ntasks=1 \
        --cpus-per-task=1 \
        srun \
            python \
                $dirname/accu_threshold_with_pcraster.py $flow_direction_raster_pathname $flux_pathname
}


# accu_threshold_with_lue
# accu_threshold_with_pcraster
