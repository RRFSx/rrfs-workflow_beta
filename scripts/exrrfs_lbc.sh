#!/usr/bin/env bash
declare -rx PS4='+ $(basename ${BASH_SOURCE[0]:-${FUNCNAME[0]:-"Unknown"}})[${LINENO}]${id}: '
set -x
cpreq=${cpreq:-cpreq}
prefix=${LBC_PREFIX:-LBC_PREFIX_not_defined}
cd ${DATA}

# generate the namelist on the fly
# required variables: init_case, start_time, end_time, nvertlevels, nsoillevels, nfglevles, nfgsoillevels,
# prefix, inerval_seconds, zeta_levels, decomp_file_prefix
init_case=9
EDATE=$($NDATE ${FHR} ${CDATE})
start_time=$(date -d "${EDATE:0:8} ${EDATE:8:2}" +%Y-%m-%d_%H:%M:%S)
end_time=${start_time}
nvertlevels=55
nsoillevels=4
if [[ "${prefix}" == "RAP" || "${prefix}" == "HRRR" ]]; then
  nfglevels=51
  nfgsoillevels=9
elif  [[ "${prefix}" == "RRFS" ]]; then
  nfglevels=66
  nfgsoillevels=9
elif  [[ "${prefix}" == "GFS" ]]; then
  nfglevels=58
  nfgsoillevels=4
elif  [[ "${prefix}" == "GEFS" ]]; then
  nfglevels=32
  nfgsoillevels=4
fi
interval_seconds=3600 # just a place holder as we use metatask to run lbc hour by hour
zeta_levels=${FIXrrfs}/meshes/L60.txt
decomp_file_prefix="${NET}.graph.info.part."
#
physics_suite=${PHYSICS_SUITE:-'PHYSICS_SUITE_not_defined'}
file_content=$(< ${PARMrrfs}/rrfs/${physics_suite}/namelist.init_atmosphere) # read in all content
eval "echo \"${file_content}\"" > namelist.init_atmosphere

# generate the streams file on the fly using sed as this file contains "filename_template='lbc.$Y-$M-$D_$h.$m.$s.nc'"
sed -e "s/@input_stream@/init.nc/" -e "s/@output_stream@/foo.nc/" \
    -e "s/@lbc_interval@/1/" ${PARMrrfs}/rrfs/streams.init_atmosphere > streams.init_atmosphere

#prepare for init_atmosphere
ln -snf ${COMINrrfs}/${RUN}.${PDY}/${cyc}/ungrib/${prefix}:${start_time:0:13} .
ln -snf ${COMINrrfs}/${RUN}.${PDY}/${cyc}/ic/init.nc .
${cpreq} ${FIXrrfs}/meshes/${NET}.static.nc static.nc
${cpreq} ${FIXrrfs}/graphinfo/${NET}.graph.info.part.${NTASKS} .

# run init_atmosphere_model
### temporarily solution since mpas model uses different modules files that other components
set +x # supress messy output in the module load process
module purge
module use ${HOMErrfs}/modulefiles
module load build/${MACHINE}.intel
module list
set -x  
### temporarily solution since mpas model uses different modules files that other components
source prep_step
srun ${EXECrrfs}/init_atmosphere_model.x
export err=$?
err_chk

# copy lbc*.nc to COMOUT
${cpreq} ${DATA}/lbc*.nc ${COMOUT}/${task_id}/
