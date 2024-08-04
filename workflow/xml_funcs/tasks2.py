#!/usr/bin/env python
import os
from xml_funcs.base import xml_task, source, get_cascade_env

### begin of ungrib_ic --------------------------------------------------------
def ungrib_ic(xmlFile, expdir):
  task_id='ungrib_ic'
  cycledefs='ic'
  # Task-specific EnVars beyond the task_common_vars
  dcTaskEnv={
    'FHR': '000',
    'TYPE': 'IC'
  }
  # dependencies
  prefix=os.getenv('IC_PREFIX','IC_PREFIX_not_defined')
  offset=os.getenv('IC_OFFSET','3')
  COMINgfs=os.getenv("COMINgfs",'COMINgfs_not_defined')
  COMINrrfs=os.getenv("COMINrrfs",'COMINrrfs_not_defined')
  COMINrap=os.getenv("COMINrap",'COMINrap_not_defined')
  COMINhrrr=os.getenv("COMINhrrr",'COMINhrrr_not_defined')
  COMINgefs=os.getenv("COMINgefs",'COMINgefs_not_defined')
  if prefix == "GFS":
    fpath=f'{COMINgfs}/gfs.@Y@m@d/@H/gfs.t@Hz.pgrb2.0p25.f{offset:>03}'
  elif prefix == "RRFS":
    fpath=f'{COMINrrfs}/rrfs.@Y@m@d/@H/rrfs.t@Hz.natlve.f{offset:>02}.grib2'
  elif prefix == "RAP":
    fpath=f'{COMINrap}/rap.@Y@m@d/rap.t@Hz.wrfnatf{offset:>02}.grib2'
  elif prefix == "GEFS":
    fpath=f'{COMINgefs}/gefs.@Y@m@d/@H/gefs.t@Hz.pgrb2.0p25.f{offset:>03}'
  else:
    fpath=f'/not_supported_LBC_PREFIX={prefix}'

  timedep=""
  realtime=os.getenv("REALTIME","false")
  starttime=get_cascade_env(f"STARTTIME_{task_id}".upper())
  if realtime.upper() == "TRUE":
    timedep=f'\n  <timedep><cyclestr offset="{starttime}">@Y@m@d@H@M00</cyclestr></timedep>'
  #
  dependencies=f'''
  <dependency>
  <and>{timedep}
  <datadep age="00:05:00"><cyclestr offset="-{offset}:00:00">{fpath}</cyclestr></datadep>
  </and>
  </dependency>'''
  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies,False,"", "", "","UNGRIB")
### end of ungrib_ic --------------------------------------------------------

### begin of ungrib_lbc --------------------------------------------------------
def ungrib_lbc(xmlFile, expdir, do_ensemble=False):
  if not do_ensemble:
    meta_id='ungrib_lbc'
    cycledefs='lbc'
    # metatask (support nested metatasks)
    fhr=os.getenv('FCST_LENGTH','12')
    offset=int(os.getenv('LBC_OFFSET','6'))
    length=int(os.getenv('LBC_LENGTH','18'))
    interval=int(os.getenv('LBC_INTERVAL','3'))
    meta_hr= ''.join(f'{i:03d} ' for i in range(0,int(length)+1,int(interval))).strip()
    comin_hr=''.join(f'{i:03d} ' for i in range(int(offset),int(length)+int(offset)+1,int(interval))).strip()
    meta_bgn=f'''
<metatask name="{meta_id}">
<var name="fhr">{meta_hr}</var>
<var name="fhr_in">{comin_hr}</var>'''
    meta_end=f'\
</metatask>\n'
  #
  else: # ensemble
    meta_id='ungrib_lbc'
    cycledefs='ens_lbc'
    # metatask (support nested metatasks)
    fhr=os.getenv('ENS_FCST_LENGTH','6')
    offset=int(os.getenv('ENS_LBC_OFFSET','36'))
    length=int(os.getenv('ENS_LBC_LENGTH','12'))
    interval=int(os.getenv('ENS_LBC_INTERVAL','3'))
    n_mem=int(os.getenv('ENS_NUM_OF_MEMBERS','2'))
    imems=''.join(f'{i:03d} ' for i in range(0,int(n_mem))).strip()
    gmems=''.join(f'{i:02d} ' for i in range(0,int(n_mem))).strip()
    meta_hr= ''.join(f'{i:03d} ' for i in range(0,int(length)+1,int(interval))).strip()
    comin_hr=''.join(f'{i:03d} ' for i in range(int(offset),int(length)+int(offset)+1,int(interval))).strip()
    meta_bgn=f'''
<metatask name=ens_{meta_id}>
<var name="imem">{imems}</var>
<var name="gmem">{gmems}</var>
<metatask name="{meta_id}_m#imem#">
<var name="fhr">{meta_hr}</var>
<var name="fhr_in">{comin_hr}</var>'''
    meta_end=f'\
</metatask>\n\
</metatask>\n'

  # Task-specific EnVars beyond the task_common_vars
  dcTaskEnv={
    'FHR': '#fhr#',
    'TYPE': 'LBC',
  }
  if not do_ensemble:
    task_id=f'{meta_id}_f#fhr#'
    prefix=os.getenv('LBC_PREFIX','GFS')
  else:
    task_id=f'{meta_id}_m#imem#_f#fhr#'
    dcTaskEnv['IMEM']="#imem#"
    prefix=os.getenv('ENS_LBC_PREFIX','GEFS')

  # dependencies
  COMINgfs=os.getenv("COMINgfs",'COMINgfs_not_defined')
  COMINrrfs=os.getenv("COMINrrfs",'COMINrrfs_not_defined')
  COMINrap=os.getenv("COMINrap",'COMINrap_not_defined')
  COMINhrrr=os.getenv("COMINhrrr",'COMINhrrr_not_defined')
  COMINgefs=os.getenv("COMINgefs",'COMINgefs_not_defined')
  if prefix == "GFS":
    fpath=f'{COMINgfs}/gfs.@Y@m@d/@H/gfs.t@Hz.pgrb2.0p25.f#fhr_in#'
  elif prefix == "RRFS":
    fpath=f'{COMINrrfs}/rrfs.@Y@m@d/@H/rrfs.t@Hz.natlve.f#fhr_in#.grib2'
  elif prefix == "RAP":
    fpath=f'{COMINrap}/rap.@Y@m@d/rap.t@Hz.wrfnatf#fhr_in#.grib2'
  elif prefix == "GEFS":
    fpath=f'{COMINgefs}/gefs.@Y@m@d/@H/gep#gmem#.t@Hz.pgrb2a.0p50.f#fhr_in#'
    fpath2=f'{COMINgefs}/gefs.@Y@m@d/@H/gep#gmem#.t@Hz.pgrb2b.0p50.f#fhr_in#'
  else:
    fpath=f'/not_supported_LBC_PREFIX={prefix}'

  timedep=""
  realtime=os.getenv("REALTIME","false")
  starttime=get_cascade_env(f"STARTTIME_{meta_id}".upper())
  if realtime.upper() == "TRUE":
    timedep=f'\n  <timedep><cyclestr offset="{starttime}">@Y@m@d@H@M00</cyclestr></timedep>'
  #
  datadep=f'<datadep age="00:05:00"><cyclestr offset="-{offset}:00:00">{fpath}</cyclestr></datadep>'
  if do_ensemble:
    datadep=datedep+f'\n  <datadep age="00:05:00"><cyclestr offset="-{offset}:00:00">{fpath2}</cyclestr></datadep>'
  dependencies=f'''
  <dependency>
  <and>{timedep}
  {datadep}
  </and>
  </dependency>'''
  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies,True,meta_id,meta_bgn,meta_end,"UNGRIB")
### end of ungrib_lbc --------------------------------------------------------

### begin of mpassit --------------------------------------------------------
def mpassit(xmlFile, expdir):
  meta_id='mpassit'
  cycledefs='prod'
  # metatask (nested or not)
  fhr=os.getenv('FCST_LENGTH','3')
  if int(fhr) >=100:
    print(f'FCST_LENGTH>=100 not supported: {fhr}')
    exit()
  #meta_hr=''.join(f'{i:03d} ' for i in range(int(fhr)+1)).strip()
  meta_hr=''.join(f'{i:03d} ' for i in range(int(fhr)+1)).strip()[4:] #remove '000 ' as no f000 diag and history files for restart cycles yet, gge.debug
  fhr2=''.join(f'{i:02d} ' for i in range(int(fhr)+1)).strip()[3:] #remove '00 '
  meta_bgn=f'''
<metatask name="{meta_id}">
<var name="fhr">{meta_hr}</var>
<var name="fhr2">{fhr2}</var>'''

  meta_end=f'\
</metatask>\n'

  # Task-specific EnVars beyond the task_common_vars
  dcTaskEnv={
    'FHR': '#fhr#',
  }
  task_id=f'{meta_id}_f#fhr#'

  timedep=""
  realtime=os.getenv("REALTIME","false")
  starttime=get_cascade_env(f"STARTTIME_{meta_id}".upper())
  if realtime.upper() == "TRUE":
    timedep=f'\n  <timedep><cyclestr offset="{starttime}">@Y@m@d@H@M00</cyclestr></timedep>'
  #
  DATAROOT=os.getenv("DATAROOT","DATAROOT_NOT_DEFINED")
  RUN='rrfs'
  NET=os.getenv("NET","NET_NOT_DEFINED")
  VERSION=os.getenv("VERSION","VERSION_NOT_DEFINED")
  dependencies=f'''
  <dependency>
  <and>{timedep}
  <datadep age="00:05:00"><cyclestr>{DATAROOT}/{NET}/{VERSION}/{RUN}.@Y@m@d/@H/fcst/</cyclestr><cyclestr offset="#fhr2#:00:00">diag.@Y-@m-@d_@H.@M.@S.nc</cyclestr></datadep>
  <datadep age="00:05:00"><cyclestr>{DATAROOT}/{NET}/{VERSION}/{RUN}.@Y@m@d/@H/fcst/</cyclestr><cyclestr offset="#fhr2#:00:00">history.@Y-@m-@d_@H.@M.@S.nc</cyclestr></datadep>
  </and>
  </dependency>'''
  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies,True,meta_id,meta_bgn,meta_end)
### end of mpassit --------------------------------------------------------

### begin of upp --------------------------------------------------------
def upp(xmlFile, expdir):
  meta_id='upp'
  cycledefs='prod'
  # metatask (nested or not)
  fhr=os.getenv('FCST_LENGTH','9')
  #meta_hr=''.join(f'{i:03d} ' for i in range(int(fhr)+1)).strip()
  meta_hr=''.join(f'{i:03d} ' for i in range(int(fhr)+1)).strip()[4:] #remove '000 ' as no f000 diag and history files for restart cycles yet, gge.debug
  meta_bgn= \
f'''
<metatask name="{meta_id}">
<var name="fhr">{meta_hr}</var>'''
  meta_end=f'\
</metatask>\n'

  # Task-specific EnVars beyond the task_common_vars
  dcTaskEnv={
    'FHR': '#fhr#',
  }
  task_id=f'{meta_id}_f#fhr#'

  timedep=""
  realtime=os.getenv("REALTIME","false")
  starttime=get_cascade_env(f"STARTTIME_{meta_id}".upper())
  if realtime.upper() == "TRUE":
    timedep=f'\n  <timedep><cyclestr offset="{starttime}">@Y@m@d@H@M00</cyclestr></timedep>'
  #
  COMROOT=os.getenv("COMROOT","COMROOT_NOT_DEFINED")
  RUN='rrfs'
  NET=os.getenv("NET","NET_NOT_DEFINED")
  VERSION=os.getenv("VERSION","VERSION_NOT_DEFINED")
  dependencies=f'''
  <dependency>
  <and>{timedep}
  <taskdep task="mpassit_f#fhr#"/>
  </and>
  </dependency>'''
  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies,True,meta_id,meta_bgn,meta_end)
### end of upp --------------------------------------------------------
