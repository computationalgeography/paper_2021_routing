#!/usr/bin/env bash
set -e


nr_nodes=1
area="africa"
input_dataset_pathname="$LUE_ROUTING_DATA/$area/africa.lue"
flow_direction_array_pathname="area/raster/ldd"

nr_nodes=1
area="pyrenees"
input_dataset_pathname="$LUE_ROUTING_DATA/$area/ldd_108680.lue"
flow_direction_array_pathname="area/raster/ldd_108680"

nr_nodes=1
>>>>>>> 01d1cafae0699d52b6b9eeb12ef21e6b329c74f0
area="south_africa"
input_dataset_pathname="$LUE_ROUTING_DATA/$area/south_africa.lue"
flow_direction_array_pathname="area/raster/ldd_southafrica"


script_pathname=$LUE/../paper_2021_routing/source/vampir/accumulate_flow.py

# PYTHONPATH=$LUE/../paper_2021_routing/source/:$PYTHONPATH

export APEX_OTF2_ARCHIVE_PATH=$HOME/tmp/trace/$(date +"%Y%m%d-%H:%M")
export APEX_OTF2=1


function run_on_eejit()
{
    # Fixed. Depends on platform.
    partition="defq"  # allq
    nr_numa_domains_per_node=1  # 8
    nr_cores_per_socket=6
    nr_threads_per_locality=$nr_cores_per_socket
    nr_cpus_per_task=12
    cpu_binding="thread:0-$(expr $nr_threads_per_locality - 1)=core:0-$(expr $nr_threads_per_locality - 1).pu:0"
    nr_localities=$(expr $nr_nodes \* $nr_numa_domains_per_node)

    export UCX_LOG_LEVEL=error

    salloc \
        --partition=$partition \
        --nodes=$nr_nodes \
        --ntasks=$nr_localities \
        --cpus-per-task=$nr_cpus_per_task \
        --cores-per-socket=$nr_cores_per_socket \
        mpirun \
            --mca btl_openib_allow_ib true \
            python \
                $script_pathname \
                    $input_dataset_pathname $flow_direction_array_pathname \
                    --hpx:ini="hpx.os_threads=$nr_threads_per_locality" \
                    --hpx:bind=$cpu_binding \
                    --hpx:print-bind
}


function run_on_desktop()
{
    nr_cores_per_socket=$1

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


run_on_desktop 4
# run_on_eejit
