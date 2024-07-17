#!/usr/bin/env bash
set -x
cpreq=${cpreq:-cpreq}
prefix='GFS'

cd ${DATA}
start_time=$(date -d "${CDATE:0:8} ${CDATE:8:2}" +%Y-%m-%d_%H:%M:%S) 
# determine whether to begin new cycles and then get ic differently
IFS=' ' read -r -a array <<< "${PROD_BGN_HRS}"
begin="NO"
for hr in "${array[@]}"; do
  if [[ "${cyc}" == "$(printf '%02d' ${hr})" ]]; then
    begin="YES"; break
  fi
done
if [[ "${begin}" == "YES" ]]; then
  ${cpreq} ${COMINrrfs}/${RUN}.${PDY}/${cyc}/ic/init.nc .
  do_restart='false'
else
  ${cpreq} ${COMINrrfs}/${RUN}.${PDY}/${cyc}/da/restart.${start_time}.nc .
  do_restart='true'
fi
offset=3
CDATElbc=$($NDATE -${offset} ${CDATE})
${cpreq} ${COMINrrfs}/${RUN}.${CDATElbc:0:8}/${CDATElbc:8:2}/lbc/lbc*.nc .
${cpreq} ${FIXrrfs}/physics/* .
ln -snf VEGPARM.TBL.fcst VEGPARM.TBL
mkdir -p graphinfo stream_list
${cpreq} ${FIXrrfs}/graphinfo/* graphinfo/
cpreq ${FIXrrfs}/stream_list/* stream_list/

# generate the namelist on the fly
# start_time, do_restart are already assigned in the above
run_duration=${FCST_LENGTH_HRS:-6}:00:00
physics_suite=${PHYSICS_SUITE:-'mesoscale_reference'}
jedi_da="false" #true
file_content=$(< ${PARMrrfs}/rrfs/namelist.atmosphere) # read in all content
eval "echo \"${file_content}\"" > namelist.atmosphere

# generate the streams file on the fly using sed as this file contains "filename_template='lbc.$Y-$M-$D_$h.$m.$s.nc'"
restart_interval=${RESTART_INTERVAL_HRS:-1}
history_interval=${HISTORY_INTERVAL_HRS:-1}
diag_interval=${DIAG_INTERVAL_HRS:-1}
lbc_interval=${LBC_INTERVAL_HRS:-3}
sed -e "s/@restart_interval@/${restart_interval}/" -e "s/@history_interval@/${history_interval}/" \
    -e "s/@diag_interval@/${diag_interval}/" -e "s/@lbc_interval@/${lbc_interval}/" \
    ${PARMrrfs}/rrfs/streams.atmosphere_fcst > streams.atmosphere

# run the MPAS model
ulimit -s unlimited
ulimit -v unlimited
ulimit -a
### temporarily solution since mpas model uses different modules files that other components
set +x # supress messy output in the module load process
module purge
module use ${HOMErrfs}/modulefiles
module load build/${MACHINE}.intel
module list
set -x  
### temporarily solution since mpas model uses different modules files that other components
source prep_step
srun ${EXECrrfs}/atmosphere_model.x 
# check the status
export err=$?
err_chk

# copy output to COMOUT
#${cpreq} ${DATA}/init.nc ${COMOUT}/${task_id}/
