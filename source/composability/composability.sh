#!/usr/bin/env bash
set -e

# Run a model with and without synchronization points between each operation. In case of
# composable operations, the latency of the run without synchronization points is smaller.

dirname="$( cd "$(dirname "$BASH_SOURCE")" ; pwd -P )"

output_prefix="$LUE_ROUTING_DATA/tmp/$area"

export UCX_LOG_LEVEL=error

# export APEX_OTF2_ARCHIVE_PATH=$HOME/tmp/trace/$(date +"%Y%m%d-%H:%M")
export APEX_OTF2_ARCHIVE_PATH=/scratch/depfg/jong0137/tmp/trace-accu/$(date +"%Y%m%d-%H:%M")
export APEX_OTF2=1
export APEX_PROFILE=1
export APEX_SCREEN_OUTPUT=1

# Merit, Afica, original (MH1)
# Same data as used in weak scalability experiment, using all 6 cores in a single NUMA node
input_dataset_pathname="$LUE_BENCHMARK_DATA/flow_accumulation/africa-1-scaling.lue"
flow_direction_array_pathname="area/raster/flow_direction"
subset_center="30000, 49200"
subset_shape="30000, 30000"

# # Merit, Africa, MH2
# # Same data as used in weak scalability experiment, using all 8 NUMA nodes in a single cluster node
# input_dataset_pathname="$LUE_BENCHMARK_DATA/flow_accumulation/africa-2-scaling.lue"
# flow_direction_array_pathname="area/raster/flow_direction"
# subset_center="60000, 98400"
# subset_shape="85000, 85000"


function run_on_eejit()
{
    export LD_PRELOAD=$GOOGLE_PERFTOOLS_ROOT/lib/libtcmalloc_minimal.so.4

    nr_nodes=1
    nr_numa_domains_per_node=8
    nr_cores_per_socket=6
    nr_cpus_per_task=12
    cpu_binding="thread:0-5=core:0-5.pu:0"
    nr_localities=$(expr $nr_nodes \* $nr_numa_domains_per_node)

    nr_localities=1

    salloc \
        --partition="allq" \
        --nodes=$nr_nodes \
        --ntasks=$nr_localities \
        --cpus-per-task=$nr_cpus_per_task \
        --cores-per-socket=$nr_cores_per_socket \
        mpirun \
            python \
                $dirname/composability.py \
                    $input_dataset_pathname $flow_direction_array_pathname \
                    "$subset_center" "$subset_shape" \
                    --hpx:ignore-batch-env --hpx:localities=$nr_localities \
                    --hpx:ini="hpx.os_threads=$nr_cores_per_socket" \
                    --hpx:bind=$cpu_binding \
                    --hpx:print-bind
}


# Running the model and postprocessing may have to be run one after the other. In case of errors,
# call this script multiple times, with one of them commented. Dll hell...

# Results will be apended to Pickle file. Remove the file in case of new experiments:
# - model changed
# - other area
# - ...
run_on_eejit

# python $dirname/postprocess.py
