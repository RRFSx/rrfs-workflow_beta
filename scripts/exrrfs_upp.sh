#!/usr/bin/env bash
declare -rx PS4='+ $(basename ${BASH_SOURCE[0]:-${FUNCNAME[0]:-"Unknown"}})[${LINENO}]${id}: '
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
### temporarily solution as UPP uses modules different from other components
set +x # supress messy output in the module load process
module purge
module use /mnt/lfs5/BMC/wrfruc/HRRRv5/UPP/modulefiles
module load jet
module use /lfs5/BMC/nrtrr/FIX_RRFS2/modulefiles
module load prod_util/2.1.1
module list
set -x  
### temporarily solution as UPP uses modules different from other components
source prep_step
srun /lfs5/BMC/nrtrr/FIX_RRFS2/exec/upp.x #gge.debug temp solution
# check the status copy output to COMOUT
wrfprs="WRFPRS${fhr}.tm00"
wrfnat="WRFNAT${fhr}.tm00"
wrftwo="WRFTWO${fhr}.tm00"
if [[ ! -s "./${wrfprs}" ]]; then
  echo "FATAL ERROR: failed to genereate WRF grib2 files"
  export err=99
  err_exit
fi

### generate final grib2 products
WGRIB2=/apps/wgrib2/2.0.8/intel/18.0.5.274/bin/wgrib2
HRRR_DIR="/public/data/grib/hrrr_wrfprs/7/0/83/0_1905141_30" #COMINhrrr
YYJJJHH=$(date -d "${CDATE:0:8} ${CDATE:8:2}:00" +%y%j%H)
# copy selected fields from netcdf to grib2, using HRRR grib2 as a template
${WGRIB2} ${HRRR_DIR}/${YYJJJHH}0000${fhr} -match ":TSOIL:" -set_grib_type simple -grib_out TSOIL_template.grib2
${WGRIB2} ${HRRR_DIR}/${YYJJJHH}0000${fhr} -match ":SOILW:" -set_grib_type simple -grib_out SOILW_template.grib2
${WGRIB2} ${HRRR_DIR}/${YYJJJHH}0000${fhr} -match ":VGTYP:" -set_grib_type simple -grib_out VGTYP.grib2
PY=/contrib/miniconda3/4.5.12/envs/avid_verify/bin/python
SCRIPTS="/lfs5/BMC/nrtrr/FIX_RRFS2/exec"
${PY} ${SCRIPTS}/netcdf_to_grib.py mpassit.${timestr}.nc TSLB TSOIL_template.grib2 TSOIL.grib2
${PY} ${SCRIPTS}/netcdf_to_grib.py mpassit.${timestr}.nc SMOIS SOILW_template.grib2 SOILW.grib2
cat ${wrftwo} TSOIL.grib2 SOILW.grib2 VGTYP.grib2 > ${wrftwo}.tmp
mv ${wrftwo}.tmp ${wrftwo}

# Append the 2D fields onto the 3D files
cat ${wrfprs} ${wrftwo} > ${wrfprs}.tmp
mv ${wrfprs}.tmp ${wrfprs}
cat ${wrfnat} ${wrftwo} > ${wrfnat}.two
mv ${wrfnat}.two ${wrfnat}

# copy products to COMOUT # file name does not comply with NCO standards #gge.debug tmp
${cpreq} ${wrfprs} ${COMOUT}/${RUN}_prs_${CDATE}_f${fhr}.grib2
${cpreq} ${wrfnat} ${COMOUT}/${RUN}_nat_${CDATE}_f${fhr}.grib2
${cpreq} ${wrftwo} ${COMOUT}/${RUN}_two_${CDATE}_f${fhr}.grib2
${cpreq} ${wrfprs} ${COMOUT}/${YYJJJHH}0000${fhr}
