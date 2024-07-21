#!/usr/bin/env bash
set -x
cpreq=${cpreq:-cpreq}
prefix=${LBC_PREFIX:-GFS}
lbc_offset=${LBC_OFFSET_HRS:-6}
lbc_interval=${LBC_INTERVAL_HRS:-3}
lbc_length=${LBC_LENGTH_HRS:-12}
nfiles=$((10#$lbc_length/10#$lbc_interval))

CDATElbc=$($NDATE -${lbc_offset} ${CDATE})

cd ${DATA}/ungrib
${cpreq} ${FIXrrfs}/Vtables/Vtable.${prefix} Vtable
for knt in $(seq 1 $((10#$nfiles+1)) ); do
  FHR=$( printf %03d $((10#$lbc_offset+(10#$knt-1)*10#$lbc_interval )) )
  ${cpreq} ${COMINgfs}/gfs.${CDATElbc:0:8}/${CDATElbc:8:2}/gfs.t${CDATElbc:8:2}z.pgrb2.0p25.f${FHR}  $(${USHrrfs}/num_to_GRIBFILE.XXX.sh ${knt})
done
#
# generate the namelist on the fly
start_time=$(date -d "${CDATE:0:8} ${CDATE:8:2}" +%Y-%m-%d_%H:%M:%S) 
EDATE=$($NDATE ${lbc_length} ${CDATE})
end_time=$(date -d "${EDATE:0:8} ${EDATE:8:2}" +%Y-%m-%d_%H:%M:%S)
interval_seconds=$((10#$lbc_interval*3600))
sed -e "s/@start_time@/${start_time}/" -e "s/@end_time@/${end_time}/" \
    -e "s/@interval_seconds@/${interval_seconds}/" \
    -e "s/@prefix@/${prefix}/" ${PARMrrfs}/rrfs/namelist.wps > namelist.wps

# run ungrib
source prep_step
${EXECrrfs}/ungrib.x
# check the status
export err=$?
err_chk

#prepare for init_atmosphere
cd ${DATA}
ln -snf ./ungrib/${prefix}* .
${cpreq} ${FIXrrfs}/meshes/${NET}.static.nc static.nc
${cpreq} ${FIXrrfs}/graphinfo/${NET}_mpas.graph.info.part.${NTASKS} .

#### generate init.nc first -------------------------------------------------------------------
#### why we need init.nc when generating lbc??
# generate the namelist on the fly
end_time=${start_time}
init_case=7
decomp_file_prefix="${NET}_mpas.graph.info.part."
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
    -e "s/@lbc_interval@/${lbc_interval}/" ${PARMrrfs}/rrfs/streams.init_atmosphere > streams.init_atmosphere

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
mv namelist.init_atmosphere namelist.init_atmosphere.ic
mv streams.init_atmosphere streams.init_atmosphere.ic

#### now generate lbc  -------------------------------------------------------------------
# genereate the namelist on the fly 
end_time=$(date -d "${EDATE:0:8} ${EDATE:8:2}" +%Y-%m-%d_%H:%M:%S)
init_case=9
file_content=$(< ${PARMrrfs}/rrfs/namelist.init_atmosphere) # read in all content
eval "echo \"${file_content}\"" > namelist.init_atmosphere

# generate the streams file on the fly using sed as this file contains "filename_template='lbc.$Y-$M-$D_$h.$m.$s.nc'"
sed -e "s/@input_stream@/init.nc/" -e "s/@output_stream@/foo.nc/" \
    -e "s/@lbc_interval@/${lbc_interval}/" ${PARMrrfs}/rrfs/streams.init_atmosphere > streams.init_atmosphere

# run init_atmosphere_model
source prep_step
srun ${EXECrrfs}/init_atmosphere_model.x
export err=$?
err_chk

# copy lbc*.nc to COMOUT
${cpreq} ${DATA}/lbc*.nc ${COMOUT}/${task_id}/
