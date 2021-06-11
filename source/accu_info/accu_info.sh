#!/usr/bin/env bash
set -e


dirname="$( cd "$(dirname "$BASH_SOURCE")" ; pwd -P )"

source $dirname/../common.sh


output_prefix="$LUE_ROUTING_DATA/tmp/$area"
lue_translate="$LUE_OBJECTS/bin/lue_translate"

export UCX_LOG_LEVEL=error


output_dataset_pathname="$output_prefix/accu_info.lue"


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
                $dirname/accu_info.py \
                    $input_dataset_pathname $flow_direction_array_pathname \
                    $output_dataset_pathname \
                    --hpx:print-bind
}


function run_on_desktop()
{
    nr_cores_per_socket=$1

    nr_nodes=1
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
            $dirname/accu_info.py \
                $input_dataset_pathname $flow_direction_array_pathname \
                $output_dataset_pathname \
                --hpx:ini="hpx.os_threads=$nr_threads_per_locality" \
                --hpx:bind=$cpu_binding \
                --hpx:print-bind
}


function post_process()
{
    layer_names="
        flow_direction
        inflow_count
        stream_class
    "

    for layer_name in $layer_names;
    do
        output_raster_pathname=$output_prefix/$layer_name.tif

        $lue_translate export -m $output_prefix/$layer_name.json \
            $output_dataset_pathname $output_raster_pathname

        gdal_edit.py -a_srs "$srs_info" $output_raster_pathname

        # extent: west north east south
        gdal_edit.py -a_ullr $extent $output_raster_pathname
    done


    layer_names="
        partition_class
        solvable_fraction
        nr_cells_to_solve
    "

    for layer_name in $layer_names;
    do
        for layer_name_i_json in $output_prefix/$layer_name*.json;
        do
            i=$(echo $layer_name_i_json | cut -d '-' -f 2 | cut -d '.' -f 1)

            output_raster_pathname=$output_prefix/$layer_name-$i.tif

            $lue_translate export -m $output_prefix/$layer_name-$i.json \
                $output_dataset_pathname $output_raster_pathname

            gdal_edit.py -a_srs "$srs_info" $output_raster_pathname

            # extent: west north east south
            gdal_edit.py -a_ullr $extent $output_raster_pathname
        done
    done
}


# run_on_desktop 4
# run_on_eejit
# post_process
