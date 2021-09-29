#!/usr/bin/bash
set -e


# Given a (resampled) DEM stored in a GDAL compatible format:
# - Import the DEM into a LUE dataset (lue_translate).
# - Read the DEM and create a flow direction network. Add the network
#   to the LUE dataset.


lue_translate="$LUE_OBJECTS/bin/lue_translate"
input_prefix=/scratch/depfg/pcraster/data/africa
output_prefix="$LUE_ROUTING_DATA/africa"


factor=3
nr_nodes=3

partition="defq"  # allq
nr_numa_domains_per_node=8
nr_cores_per_socket=6
nr_cpus_per_task=12
cpu_binding="thread:0-5=core:0-5.pu:0"
nr_localities=$(expr $nr_nodes \* $nr_numa_domains_per_node)


# srun \
#     --partition=$partition \
#     --nodes=1 \
#     $lue_translate import $output_prefix/africa-${factor}.lue $input_prefix/factor${factor}.vrt


export LD_PRELOAD=$GOOGLE_PERFTOOLS_ROOT/lib/libtcmalloc_minimal.so.4

salloc \
    --partition=$partition \
    --nodes=$nr_nodes \
    --ntasks=$nr_localities \
    --cpus-per-task=$nr_cpus_per_task \
    --cores-per-socket=$nr_cores_per_socket \
    mpirun \
        python \
            $LUE/../paper_2021_routing/source/resample/create_flow_direction_network.py \
                $output_prefix/africa-${factor}.lue "area/raster/factor${factor}" \
                $output_prefix/africa-${factor}-scaling.lue \
                --hpx:ini="hpx.os_threads=$nr_cores_per_socket" \
                --hpx:bind=$cpu_binding \
                --hpx:print-bind
