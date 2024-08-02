#!/usr/bin/env bash
declare -rx PS4='+ $(basename ${BASH_SOURCE[0]:-${FUNCNAME[0]:-"Unknown"}})[${LINENO}]${id}: '
set -x
cpreq=${cpreq:-cpreq}
cd ${DATA}

# link the prepbufr file
ln -snf ${OBSINprepbufr}/${CDATE}.rap.t${cyc}z.prepbufr.tm00 prepbufr
ln -snf ${EXECrrfs}/bufr2ioda.x .

# generate the namelist on the fly
REFERENCE_TIME=${REFERENCE_TIME:-REFERENCE_TIME_not_defined}
yaml_list=(
"prepbufr_aircraft.yaml" 
"prepbufr_ascatw.yaml" 
"prepbufr_gpsipw.yaml" 
"prepbufr_mesonet.yaml" 
"prepbufr_profiler.yaml" 
"prepbufr_rassda.yaml" 
"prepbufr_satwnd.yaml" 
"prepbufr_surface.yaml" 
#"prepbufr_upperair.yaml"  # upperair has a problem gge.debug
)

# run bufr2ioda.x
for yaml in ${yaml_list[@]}; do
 sed -e "s/@reference_time@/${REFERENCE_TIME}/" ${PARMrrfs}/rrfs/${yaml} > ${yaml}
 source prep_step
 srun ./bufr2ioda.x ${yaml}
 export err=$?
 err_chk
done

# copy ioda*.nc to COMOUT
${cpreq} ${DATA}/ioda*.nc ${COMOUT}/${task_id}/${subdir}
