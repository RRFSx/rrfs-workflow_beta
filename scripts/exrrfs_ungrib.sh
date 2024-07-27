#!/usr/bin/env bash
export PS4="+ $(basename ${BASH_SOURCE})[${LINENO}]:"
set -x
cpreq=${cpreq:-cpreq}
if [[ "${TYPE}" == "IC" ]] || [[ "${TYPE}" == "ic" ]]; then
  prefix=${IC_PREFIX:-IC_PREFIX_not_defined}
  offset=${IC_OFFSET_HRS:-3}
else #lbc
  prefix=${LBC_PREFIX:-LBC_PREFIX_not_defined}
  offset=${LBC_OFFSET_HRS:-6}
fi
CDATEin=$($NDATE -${offset} ${CDATE}) #CDATEinput
FHRin=$(( 10#${FHR}+10#${offset} )) #FHRinput

cd ${DATA}
${cpreq} ${FIXrrfs}/Vtables/Vtable.${prefix} Vtable
#
# preprocess grib2 files if it is RAP or RRFS
WGRIB2=/apps/wgrib2/2.0.8/intel/18.0.5.274/bin/wgrib2
if [[ "${prefix}" == "GFS" ]]; then
  fstr=$(printf %03d ${FHRin})
  ${cpreq} ${COMINgfs}/gfs.${CDATEin:0:8}/${CDATEin:8:2}/gfs.t${CDATEin:8:2}z.pgrb2.0p25.f${fstr} GRIBFILE.AAA
elif [[ "${prefix}" == "RAP" ]]; then
  fstr=$(printf %02d ${FHRin})
  GRIBFILE=${COMINrap}/rap.${CDATEin:0:8}/rap.t${CDATEin:8:2}z.wrfnatf${fstr}.grib2
  # Interpolate to Lambert conformal grid
  if true; then #gge.debug need to confirm when to do an interpolation for RAP and RRFS
    ln -snf ${GRIBFILE} GRIBFILE.AAA
  else
    grid_specs_20km="lambert:-97.5:38.5 -133.174:449:20000.0 5.47114:299:20000.0"
    ${WGRIB2} ${GRIBFILE} -set_bitmap 1 -set_grib_type c3 -new_grid_winds grid \
           -new_grid_vectors "UGRD:VGRD:USTM:VSTM:VUCSH:VVCSH"               \
           -new_grid_interpolation neighbor                                  \
           -new_grid ${grid_specs_20km} tmp.grib2
    # Merge vector field records
    ${WGRIB2} tmp.grib2 -new_grid_vectors "UGRD:VGRD:USTM:VSTM:VUCSH:VVCSH" -submsg_uv 20km_grid.grib2
    ln -snf 20km_grid.grib2 GRIBFILE.AAA
  fi #skip preprocessing

elif [[ "${prefix}" == "RRFS" ]]; then
  fstr=$(printf %02d ${FHRin})
  GRIBFILE=${COMINrrfs1}/rrfs_a.${CDATEin:0:8}/${CDATEin:8:2}/rrfs.t${CDATEin:8:2}z.natlve.f${fstr}.grib2
  # variation on the 130 grid at 3 km
  grid_specs="lambert:266:25.000000 234.862000:2000:3000.000000 17.281000:1480:3000.000000"
  ${WGRIB2} ${GRIBFILE} -set_bitmap 1 -set_grib_type c3 -new_grid_winds grid \
	 -new_grid_vectors "UGRD:VGRD:USTM:VSTM:VUCSH:VVCSH"               \
	 -new_grid_interpolation bilinear \
	 -if "`cat ${FIXrrfs}/ungrib/budget_fields.txt`" -new_grid_interpolation budget -fi \
	 -if "`cat ${FIXrrfs}/ungrib/neighbor_fields.txt`" -new_grid_interpolation neighbor -fi \
	 -new_grid ${grid_specs} tmp.grib2
  # Merge vector field records
  ${WGRIB2} tmp.grib2 -new_grid_vectors "UGRD:VGRD:USTM:VSTM:VUCSH:VVCSH" -submsg_uv tmp2.grib2
  if [[ -s tmp2.grib2 ]]; then
    ln -snf tmp2.grib2 GRIBFILE.AAA
  else
    echo "tmp2.grib2 not created; exiting"
    export err=99; err_chk
  fi
fi
#
# generate the namelist on the fly
CDATEout=$($NDATE ${FHR} ${CDATE})
start_time=$(date -d "${CDATEout:0:8} ${CDATEout:8:2}" +%Y-%m-%d_%H:%M:%S) 
end_time=${start_time}
interval_seconds=3600
if [[ "${NET}" == "conus3km"   ]]; then
  dx=3; dy=3
else
  dx=12; dy=12
fi
sed -e "s/@start_time@/${start_time}/" -e "s/@end_time@/${end_time}/" \
    -e "s/@interval_seconds@/${interval_seconds}/" -e "s/@prefix@/${prefix}/" \
    -e "s/@dx@/${dx}/" -e "s/@dy@/${dy}/" ${PARMrrfs}/rrfs/namelist.wps > namelist.wps

# run ungrib
source prep_step
${EXECrrfs}/ungrib.x
# check the status
outfile="${prefix}:$(date -d "${CDATEout:0:8} ${CDATEout:8:2}" +%Y-%m-%d_%H)"
if [[ -s ${outfile} ]]; then
  ${cpreq} ${DATA}/${outfile} ${COMOUT}/${task_id}/
else
  echo "FATAR ERROR: ungrib failed"
  export err=99
  err_chk
fi
