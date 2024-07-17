#!/usr/bin/env bash
set -x
cpreq=${cpreq:-cpreq}
prefix=${IC_PREFIX:-GFS}
ic_offset=${IC_OFFSET_HRS:-3}
FHR=$(printf %03d ${ic_offset})
CDATEic=$($NDATE -${FHR} ${CDATE})

cd ${DATA}/ungrib
${cpreq} ${FIXrrfs}/Vtables/Vtable.${prefix} Vtable
${cpreq} ${COMINgfs}/gfs.${CDATEic:0:8}/${CDATEic:8:2}/gfs.t${CDATEic:8:2}z.prb2.0p25.f${FHR} GRIBFILE.AAA
#
# generate the namelist on the fly
start_time=$(date -d "${CDATE:0:8} ${CDATE:8:2}" +%Y-%m-%d_%H:%M:%S) 
end_time=${start_time}
interval_seconds=3600
sed -e "s/@start_time@/${start_time}/" -e "s/@end_time@/${end_time}/" \
    -e "s/@interval_seconds@/${interval_seconds}/" \
    -e "s/@prefix@/${prefix}/" ${PARMrrfs}/rrfs/namelist.wps > namelist.wps

# run ungrib
source prep_step
${EXECrrfs}/ungrib.x
# check the status
#outfile=${prefix}:$(date -d "${CDATE:0:8} ${CDATE:8:2}" +%Y-%m-%d_%H)
export err=$?
err_chk

#prepare for init_atmosphere
cd ${DATA}
ln -snf ./ungrib/${prefix}:${start_time:0:13} .
${cpreq} ${FIXrrfs}/meshes/static.nc .
${cpreq} ${FIXrrfs}/graphinfo/conus12km_mpas.graph.info.part.${NTASKS} .

# genereate the namelist on the fly
init_case=7
decomp_file_prefix='conus12km_mpas.graph.info.part.'
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

file_content=$(< ${PARMrrfs}/rrfs/namelist.init_atmosphere) # read in all content
eval "echo \"${file_content}\"" > namelist.init_atmosphere

# generate the streams file on the fly using sed as this file contains "filename_template='lbc.$Y-$M-$D_$h.$m.$s.nc'"
sed -e "s/@input_stream@/static.nc/" -e "s/@output_stream@/init.nc/" \
    -e "s/@lbc_interval@/3/" ${PARMrrfs}/rrfs/streams.init_atmosphere > streams.init_atmosphere

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

# copy init.nc to COMOUT
${cpreq} ${DATA}/init.nc ${COMOUT}/${task_id}/
