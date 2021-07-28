#!/usr/bin/env bash
set -e


dirname="$( cd "$(dirname "$BASH_SOURCE")" ; pwd -P )"

source $dirname/../common.sh

output_prefix="$LUE_ROUTING_DATA/tmp/$area"

export UCX_LOG_LEVEL=error


function run_on_eejit()
{
    export LD_PRELOAD=$GOOGLE_PERFTOOLS_ROOT/lib/libtcmalloc_minimal.so.4

    partition="defq"
    nr_nodes=1
    nr_numa_domains_per_node=8
    nr_cores_per_socket=6
    nr_cpus_per_task=12
    cpu_binding="thread:0-5=core:0-5.pu:0"
    nr_localities=$(expr $nr_nodes \* $nr_numa_domains_per_node)


    salloc \
        --partition=$partition \
        --nodes=$nr_nodes \
        --ntasks=$nr_localities \
        --cpus-per-task=$nr_cpus_per_task \
        --cores-per-socket=$nr_cores_per_socket \
        mpirun \
            python \
                $dirname/composability.py \
                    $input_dataset_pathname $flow_direction_array_pathname \
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
# run_on_eejit

python $dirname/postprocess.py
