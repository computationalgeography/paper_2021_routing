#!/usr/bin/env bash
set -e

lue_translate="$LUE_OBJECTS/bin/lue_translate"

area="pyrenees"

# input_dataset_pathname="/mnt/data1/home/kor/data/project/routing/dem_ldd/108680/ldd_108680.lue"
# flow_direction_array_pathname="area/raster/ldd_108680"

# input_dataset_pathname="/mnt/data1/home/kor/data/project/routing/africa/africa.lue"
# flow_direction_array_pathname="area/raster/flow_direction"

# input_dataset_pathname="/mnt/data1/home/kor/data/project/routing/africa2/ldd_africa.lue"
# flow_direction_array_pathname="area/raster/ldd"

input_dataset_pathname="$LUE_ROUTING_DATA/$area/ldd_108680.lue"
flow_direction_array_pathname="area/raster/ldd_108680"

output_prefix="$LUE_ROUTING_DATA/tmp"
output_dataset_pathname="$output_prefix/tmp.lue"


# NOTE: using multiple localities requires a build of LUE with support for
#     parallel I/O

nr_localities=1
nr_threads_per_locality=4

PYTHONPATH=$LUE/../paper_2021_routing/source/:$PYTHONPATH \
    `which python` $LUE_OBJECTS/_deps/hpx-build/bin/hpxrun.py \
        --localities=$nr_localities \
        --thread=$nr_threads_per_locality \
        --runwrapper=mpi \
        --parcelport=mpi \
        --verbose \
        `which python` -- $LUE/../paper_2021_routing/source/accumulate_flow.py \
            $input_dataset_pathname $flow_direction_array_pathname \
            $output_dataset_pathname


### # Fixed. Depends on platform.
### nr_numa_domains_per_node=8
### nr_cores_per_socket=6
### nr_cpus_per_task=12
### cpu_binding="thread:0-5=core:0-5.pu:0"
### 
### # Depends on size of job
### nr_nodes=2
### 
### # Fixed
### nr_tasks=$(expr $nr_nodes \* $nr_numa_domains_per_node)
### 
### 
### srun \
###     --ntasks $nr_tasks \
###     --cpus-per-task=$nr_cpus_per_task \
###     --cores-per-socket=$nr_cores_per_socket \
###     --kill-on-bad-exit \
###     python $LUE/../paper_2021_routing/source/accumulate_flow.py \
###         $input_dataset_pathname $flow_direction_array_pathname \
###         $output_dataset_pathname \
###         --hpx:ini="hpx.parcel.mpi.enable=1" \
###         --hpx:ini="hpx.os_threads=$nr_cores_per_socket" \
###         --hpx:bind=$cpu_binding \
###         --hpx:print-bind


# Post-processing
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
