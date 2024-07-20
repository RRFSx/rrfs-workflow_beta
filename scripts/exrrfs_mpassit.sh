#!/usr/bin/env bash
set -x
cpreq=${cpreq:-cpreq}

cd ${DATA}
fhr=$((10#${FHR:-0})) # remove leading zeros
CDATEp=$($NDATE ${fhr} ${CDATE} )
timestr=$(date -d "${CDATEp:0:8} ${CDATEp:8:2}" +%Y-%m-%d_%H.%M.%S) 

${cpreq} ${COMINrrfs}/${RUN}.${PDY}/${HH}/fcst/history.*.nc .
${cpreq} ${COMINrrfs}/${RUN}.${PDY}/${HH}/fcst/diag.*.nc .
${cpreq} ${FIXrrfs}/mpassit/* .
# generate the namelist on the fly
sed -e "s/@timestr@/${timestr}/" ${PARMrrfs}/rrfs/namelist.mpassit > namelist.mpassit

# run the MPAS model
ulimit -s unlimited
ulimit -v unlimited
ulimit -a
### temporarily solution since mpassit uses different modules files that other components
set +x # supress messy output in the module load process
module purge
module load gnu
module load intel/2023.2.0
module load impi/2023.2.0
module load pnetcdf/1.12.3
module load szip
module load hdf5parallel/1.10.5
module load netcdf-hdf5parallel/4.7.0
module use /mnt/lfs4/HFIP/hfv3gfs/nwprod/NCEPLIBS/modulefiles
module load netcdf/4.7.0
PNETCDF=/apps/pnetcdf/1.12.3/intel_2023.2.0-impi
module list
set -x  
### temporarily solution since mpassit uses different modules files that other components
source prep_step
srun /lfs5/BMC/nrtrr/FIX_RRFS2/exec/mpassit.x namelist.mpassit  #gge.debug temp solution
# check the status
if [[ -s './log.atmosphere.0000.err' ]]; then
  echo "FATAL ERROR: MPAS model run failed"
  export err=99
  err_exit
fi

# copy output to COMOUT
#CDATEp1=$($NDATE 1 ${CDATE})
#timestr=$(date -d "${CDATEp1:0:8} ${CDATEp1:8:2}" +%Y-%m-%d_%H.%M.%S) 
#${cpreq} ${DATA}/restart.${timestr}.nc ${COMOUT}/${task_id}/
