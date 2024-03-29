#!/usr/bin/env bash
set -e
set -x


dirname="$( cd "$(dirname "$BASH_SOURCE")" ; pwd -P )"

source $dirname/../common.sh

script_pathname=$LUE/../paper_2021_routing/source/vampir/accumulate_flow.py

# export APEX_OTF2_ARCHIVE_PATH=$HOME/tmp/trace/$(date +"%Y%m%d-%H:%M")
# export APEX_OTF2_ARCHIVE_PATH=/scratch/depfg/jong0137/tmp/trace-accu/$(date +"%Y%m%d-%H:%M")
# export APEX_OTF2=1
# export APEX_PROFILE=1
# export APEX_SCREEN_OUTPUT=1


function run_on_eejit()
{
    export LD_PRELOAD=$GOOGLE_PERFTOOLS_ROOT/lib/libtcmalloc_minimal.so.4

    # Fixed. Depends on platform.
    partition="defq"
    nr_nodes=1
    nr_numa_domains_per_node=2  # 8
    nr_cores_per_socket=6
    nr_threads_per_locality=$nr_cores_per_socket
    nr_cpus_per_task=12
    cpu_binding="thread:0-$(expr $nr_threads_per_locality - 1)=core:0-$(expr $nr_threads_per_locality - 1).pu:0"
    nr_localities=$(expr $nr_nodes \* $nr_numa_domains_per_node)

    # export UCX_LOG_LEVEL=error
    # --hpx:ini="hpx.thread_queue.min_tasks_to_steal_staged=1000"
    # --hpx:ini="hpx.thread_queue.min_tasks_to_steal_pending=1000"
    # --hpx:bind=$cpu_binding 

    salloc \
        --partition=$partition \
        --nodes=$nr_nodes \
        --ntasks=$nr_localities \
        --cpus-per-task=$nr_cpus_per_task \
        --cores-per-socket=$nr_cores_per_socket \
        mpirun \
            python \
                $script_pathname \
                    $input_dataset_pathname $flow_direction_array_pathname \
                    --hpx:ini="hpx.os_threads=$nr_threads_per_locality" \
                    --hpx:print-bind
}


function run_on_desktop()
{
    nr_cores_per_socket=$1
    nr_nodes=1

    # Fixed. Depends on platform.
    nr_numa_domains_per_node=1
    nr_threads_per_locality=$nr_cores_per_socket
    cpu_binding="thread:0-$(expr $nr_threads_per_locality - 1)=core:0-$(expr $nr_threads_per_locality - 1).pu:0"
    nr_localities=$(expr $nr_nodes \* $nr_numa_domains_per_node)

    python $LUE_OBJECTS/_deps/hpx-build/bin/hpxrun.py \
        --localities=$nr_localities \
        --thread=$nr_threads_per_locality \
        --parcelport=tcp \
        --verbose \
        `which python` -- \
            $script_pathname \
                $input_dataset_pathname $flow_direction_array_pathname \
                --hpx:ini="hpx.os_threads=$nr_threads_per_locality" \
                --hpx:bind=$cpu_binding \
                --hpx:print-bind
}


# run_on_desktop 4
run_on_eejit
