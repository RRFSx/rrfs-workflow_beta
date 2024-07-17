#!/usr/bin/env bash
set -x
cpreq=${cpreq:-cpreq}
prefix='GFS'
BUMPLOC=${BUMPLOC:-"conus12km-401km11levels"}

cd ${DATA}
${cpreq} ${FIXrrfs}/physics/* .
mkdir -p graphinfo stream_list
${cpreq} ${FIXrrfs}/graphinfo/* graphinfo/
${cpreq} ${FIXrrfs}/jedi/obsop_name_map.yaml .                  
${cpreq} ${FIXrrfs}/jedi/keptvars.yaml .              
${cpreq} ${FIXrrfs}/jedi/geovars.yaml . 
cpreq ${FIXrrfs}/stream_list/* stream_list/
mkdir -p data; cd data                   
mkdir -p bumploc bkg obs ens
${cpreq} ${FIXrrfs}/fix/bumploc/${BUMPLOC} bumploc/
${cpreq} ${FIXrrfs}/meshes/static.nc .
#${cpreq} ${COMINrrfs}/..../restart.2024-05-27_00.00.00.nc .  
#${cpreq} ${COMINioda}/..../obs/* obs/                            
#${cpreq} ${COMINgdas}/..../ens/* ens/
#
# generate the namelist on the fly
# namelist.atmosphere and streams.atmosphere
#sed -e "s/@restart_interval@/${restart_interval}/" -e "s/@history_interval@/${history_interval}/" \
#    -e "s/@diag_interval@/${diag_interval}/" -e "s/@lbc_interval@/${lbc_interval}/" \
#    ${PARMrrfs}/rrfs/streams.atmosphere_fcst > streams.atmosphere

# run mpasjedi_variational.x
export OOPS_TRACE=1
export OMP_NUM_THREADS=1
ulimit -s unlimited
ulimit -v unlimited
ulimit -a

source prep_step
#srun -l ${EXECrrfs}/mpasjedi_variational.x  ./$inputfile    log.out
# check the status
export err=$?
err_chk

# copy output to COMOUT
#${cpreq} ${DATA}/init.nc ${COMOUT}/${task_id}/
