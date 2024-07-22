#!/usr/bin/env python
import os
from xml_funcs.base import xml_task, source, get_cascade_env

### begin of mpassit --------------------------------------------------------
def mpassit(xmlFile, expdir):
  meta_id='mpassit'
  cycledefs='prod'
  # metatask (nested or not)
  fhr=os.getenv('FCST_LENGTH_HRS','3')
  #meta_hr=''.join(f'{i:03d} ' for i in range(int(fhr)+1)).strip()
  meta_hr=''.join(f'{i:03d} ' for i in range(int(fhr)+1)).strip()[4:] #remove '000 ' as no f000 diag and history files for restart cycles, gge.debug
  meta_bgn= \
f'''
<metatask name="{meta_id}">
<var name="fhr">{meta_hr}</var>'''
    #  <metatask name="{meta_id}_f#fhr#">
    #  <var name="mem">ctl</var>
    #  <var name="mp_scheme">mp_thompson</var>
    #    <task name="{meta_id}_#mem#_f#fhr#" cycledefs="fcst,fcst_long" maxtries="3">
    #    </task>
    #  </metatask>
    #</metatask>

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
  RUN=os.getenv("RUN","RUN_NOT_DEFINED")
  NET=os.getenv("NET","NET_NOT_DEFINED")
  VERSION=os.getenv("VERSION","VERSION_NOT_DEFINED")
  dependencies=f'''
  <dependency>
  <and>{timedep}
  <datadep age="00:05:00"><cyclestr>{DATAROOT}/{NET}/{VERSION}/{RUN}.@Y@m@d/@H/fcst/</cyclestr><cyclestr offset="#fhr#:00:00">diag.@Y-@m-@d_@H.@M.@S.nc</cyclestr></datadep>
  <datadep age="00:05:00"><cyclestr>{DATAROOT}/{NET}/{VERSION}/{RUN}.@Y@m@d/@H/fcst/</cyclestr><cyclestr offset="#fhr#:00:00">history.@Y-@m-@d_@H.@M.@S.nc</cyclestr></datadep>
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
  fhr=os.getenv('FCST_LENGTH_HRS','9')
  #meta_hr=''.join(f'{i:03d} ' for i in range(int(fhr)+1)).strip()
  meta_hr=''.join(f'{i:03d} ' for i in range(int(fhr)+1)).strip()[4:] #remove '000 ' as no f000 diag and history files for restart cycles, gge.debug
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
  RUN=os.getenv("RUN","RUN_NOT_DEFINED")
  NET=os.getenv("NET","NET_NOT_DEFINED")
  VERSION=os.getenv("VERSION","VERSION_NOT_DEFINED")
  dependencies=f'''
  <dependency>
  <and>{timedep}
  <datadep age="00:05:00"><cyclestr>{COMROOT}/{NET}/{VERSION}/{RUN}.@Y@m@d/@H/mpassit/</cyclestr><cyclestr offset="#fhr#:00:00">mpassit.@Y-@m-@d_@H.@M.@S.nc</cyclestr></datadep>
  </and>
  </dependency>'''
  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies,True,meta_id,meta_bgn,meta_end)
### end of upp --------------------------------------------------------
