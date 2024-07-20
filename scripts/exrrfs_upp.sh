#!/usr/bin/env bash
set -x
cpreq=${cpreq:-cpreq}

cd ${DATA}/${FHR}
fhr=$((10#${FHR:-0})) # remove leading zeros
CDATEp=$($NDATE ${fhr} ${CDATE} )
timestr=$(date -d "${CDATEp:0:8} ${CDATEp:8:2}" +%Y-%m-%d_%H.%M.%S) 

${cpreq} ${COMINrrfs}/${RUN}.${PDY}/${cyc}/mpassit/mpassit.${timestr}.nc .
${cpreq} ${FIXrrfs}/upp/* .
FIXcrtm=/mnt/lfs4/HFIP/hfv3gfs/nwprod/hpc-stack/libs/intel-18.0.5.274/crtm/2.4.0/fix #gge.debug temp soultin
while read line; do
  ln -snf ${FIXcrtm}/${line} .
done < crtmfiles.upp
# generate the namelist on the fly
cat << EOF > itag
&model_inputs
fileName='mpassit.${timestr}.nc'
fileNameFlux='mpassit.${timestr}.nc'
IOFORM='netcdfpara'
grib='grib2'
DateStr='${timestr}'
MODELNAME='RAPR'
fileNameFlat='postxconfig-NT.txt'
/
&nampgb
numx=2
/
EOF

# run the MPAS model
ulimit -s unlimited
ulimit -v unlimited
ulimit -a
### temporarily solution since upp uses modules files different from other components
set +x # supress messy output in the module load process
module purge
module use /mnt/lfs5/BMC/wrfruc/HRRRv5/UPP/modulefiles
module load jet
module use /lfs5/BMC/nrtrr/FIX_RRFS2/modulefiles
module load prod_util/2.1.1
module list
set -x  
### temporarily solution since mpassit uses different modules files that other components
source prep_step
srun /lfs5/BMC/nrtrr/FIX_RRFS2/exec/upp.x #gge.debug temp solution
# check the status copy output to COMOUT
if [[ -s "./geguoqing" ]]; then
  ${cpreq} ${DATA}/${FHR}/mpassit.${timestr}.nc ${COMOUT}/${task_id}/
else
  echo "FATAL ERROR: failed to genereate mpassit.${timestr}.nc"
  export err=99
  err_exit
fi

### generate other grib2 files
WGRIB2=/apps/wgrib2/2.0.8/intel/18.0.5.274/bin/wgrib2
PY4GRIB=/contrib/miniconda3/4.5.12/envs/avid_verify/bin/python
