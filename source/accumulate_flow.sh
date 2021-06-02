#!/usr/bin/env bash
set -e

lue_translate="$LUE_OBJECTS/bin/lue_translate"


nr_nodes=1
area="pyrenees"
input_dataset_pathname="$LUE_ROUTING_DATA/$area/ldd_108680.lue"
flow_direction_array_pathname="area/raster/ldd_108680"

nr_nodes=1
area="south_africa"
input_dataset_pathname="$LUE_ROUTING_DATA/$area/south_africa.lue"
flow_direction_array_pathname="area/raster/ldd_southafrica"

nr_nodes=1
area="africa"
input_dataset_pathname="$LUE_ROUTING_DATA/$area/africa.lue"
flow_direction_array_pathname="area/raster/ldd"


output_prefix="$LUE_ROUTING_DATA/tmp"
output_dataset_pathname="$output_prefix/$area.lue"


# PYTHONPATH=$LUE/../paper_2021_routing/source/:$PYTHONPATH \


# Fixed. Depends on platform.
partition="defq"  # allq
nr_numa_domains_per_node=8
nr_cores_per_socket=6
nr_cpus_per_task=12
cpu_binding="thread:0-5=core:0-5.pu:0"

# Depends on size of job

# Fixed
nr_localities=$(expr $nr_nodes \* $nr_numa_domains_per_node)


# Doc bug:
# - hpx.component_path → hpx.component_paths

# https://www.open-mpi.org/faq/?category=openfabrics#ofa-device-error
# https://www.open-mpi.org/faq/?category=openfabrics#ib-locked-pages
# https://www.open-mpi.org/faq/?category=openfabrics#ib-locked-pages-more


export UCX_LOG_LEVEL=error

salloc \
    --partition=$partition \
    --nodes=$nr_nodes \
    --ntasks=$nr_localities \
    --cpus-per-task=$nr_cpus_per_task \
    --cores-per-socket=$nr_cores_per_socket \
    mpirun \
        python \
            $LUE/../paper_2021_routing/source/accumulate_flow.py \
                $input_dataset_pathname $flow_direction_array_pathname \
                $output_dataset_pathname \
                --hpx:ini="hpx.os_threads=$nr_cores_per_socket" \
                --hpx:bind=$cpu_binding \
                --hpx:print-bind


# # Post-processing
# layer_names="
#     flow_direction
#     inflow_count
#     inter_partition_stream
#     flow_accumulation
#     flow_accumulation_fraction_flux
#     flow_accumulation_fraction_state
# "
# 
# for layer_name in $layer_names;
# do
#     $lue_translate export -m $output_prefix/$layer_name.json \
#         $output_dataset_pathname $output_prefix/$layer_name.tif
# done
