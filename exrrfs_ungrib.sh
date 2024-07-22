#!/usr/bin/env bash
set -x
cpreq=${cpreq:-cpreq}
prefix=${IC_PREFIX:-GFS}
ic_offset=${IC_OFFSET_HRS:-3}
FHR=$(printf %03d ${ic_offset})
CDATEic=$($NDATE -${FHR} ${CDATE})

cd ${DATA}/ungrib
${cpreq} ${FIXrrfs}/Vtables/Vtable.${prefix} Vtable
#
# preprocess grib2 files if it is RAP or RRFS
WGRIB2=/apps/wgrib2/2.0.8/intel/18.0.5.274/bin/wgrib2
if [[ "${prefix}" == "GFS" ]]; then
  ${cpreq} ${COMINgfs}/gfs.${CDATEic:0:8}/${CDATEic:8:2}/gfs.t${CDATEic:8:2}z.pgrb2.0p25.f${FHR} GRIBFILE.AAA
elif [[ "${prefix}" == "RAP" ]]; then
  FHR=$(printf %02d ${ic_offset})
  GRIB_FILE=${COMINrap}/rap.${CDATEic:0:8}/rap.t${CDATEic:8:2}z.wrfnatf${FHR}.grib2
  # Interpolate to Lambert conformal grid
  grid_specs_20km="lambert:-97.5:38.5 -133.174:449:20000.0 5.47114:299:20000.0"
  ${WGRIB2} ${GRIB_FILE} -set_bitmap 1 -set_grib_type c3 -new_grid_winds grid \
	 -new_grid_vectors "UGRD:VGRD:USTM:VSTM:VUCSH:VVCSH"               \
	 -new_grid_interpolation neighbor                                  \
	 -new_grid ${grid_specs_20km} tmp.grib2
  # Merge vector field records
  ${WGRIB2} tmp.grib2 -new_grid_vectors "UGRD:VGRD:USTM:VSTM:VUCSH:VVCSH" -submsg_uv 20km_grid.grib2
  ln -snf 20km_grid.grib2 GRIBFILE.AAA

elif [[ "${prefix}" == "RRFS" ]]; then
  FHR=$(printf %02d ${ic_offset})
  GRIB_FILE=${COMINrrfs1}/rrfs_a.${CDATEic:0:8}/${CDATEic:8:2}/rrfs.t${CDATEic:8:2}z.natlve.f${FHR}.grib2
  # variation on the 130 grid at 3 km
  grid_specs="lambert:266:25.000000 234.862000:2000:3000.000000 17.281000:1480:3000.000000"
  ${WGRIB2} ${GRIB_FILE} -set_bitmap 1 -set_grib_type c3 -new_grid_winds grid \
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
${cpreq} ${FIXrrfs}/meshes/${NET}.static.nc static.nc
${cpreq} ${FIXrrfs}/graphinfo/${NET}_mpas.graph.info.part.${NTASKS} .

# genereate the namelist on the fly
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
zeta_levels=${FIXrrfs}/meshes/L60.txt
physics_suite=${PHYSICS_SUITE:-'PHYSICS_SUITE_not_defined'}
file_content=$(< ${PARMrrfs}/rrfs/${physics_suite}/namelist.init_atmosphere) # read in all content
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
