#!/usr/bin/env python
import os
from xml_funcs.base import xml_task, source, get_cascade_env

### begin of ic --------------------------------------------------------
def ic(xmlFile, expdir):
  task_id='ic'
  cycledefs='ic,lbc' #don't know why we need init.nc for the lbc process but live with it right now
  # Task-specific EnVars beyond the task_common_vars
  dcTaskEnv={}

  # dependencies
  timedep=""
  realtime=os.getenv("REALTIME","false")
  starttime=get_cascade_env(f"STARTTIME_{task_id}".upper())
  if realtime.upper() == "TRUE":
    timedep=f'\n  <timedep><cyclestr offset="{starttime}">@Y@m@d@H@M00</cyclestr></timedep>'
  dependencies=f'''
  <dependency>
  <and>{timedep}
  <or>
    <taskdep task="ungrib_ic"/>
    <taskdep task="ungrib_lbc_f000"/>
  </or>
  </and>
  </dependency>'''
  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies)
### end of ic --------------------------------------------------------

### begin of lbc --------------------------------------------------------
def lbc(xmlFile, expdir):
  meta_id='lbc'
  cycledefs='lbc'
  # metatask (nested or not)
  fhr=os.getenv('FCST_LENGTH','12')
  offset=int(os.getenv('LBC_OFFSET','6'))
  length=int(os.getenv('LBC_LENGTH','18'))
  interval=int(os.getenv('LBC_INTERVAL','3'))
  meta_hr= ''.join(f'{i:03d} ' for i in range(0,int(length)+1,int(interval))).strip()
  comin_hr=''.join(f'{i:03d} ' for i in range(int(offset),int(length)+int(offset)+1,int(interval))).strip()
  meta_bgn=f'''
<metatask name="{meta_id}">
<var name="fhr">{meta_hr}</var>'''
  meta_end=f'\
</metatask>\n'
  task_id=f'{meta_id}_f#fhr#'

  # Task-specific EnVars beyond the task_common_vars
  dcTaskEnv={
    'FHR': '#fhr#',
  }

  # dependencies
  timedep=""
  realtime=os.getenv("REALTIME","false")
  starttime=get_cascade_env(f"STARTTIME_{task_id}".upper())
  if realtime.upper() == "TRUE":
    timedep=f'\n  <timedep><cyclestr offset="{starttime}">@Y@m@d@H@M00</cyclestr></timedep>'
  dependencies=f'''
  <dependency>
  <and>{timedep}
  <taskdep task="ungrib_lbc_f#fhr#"/>
  <taskdep task="ic"/>
  </and>
  </dependency>'''
  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies,True,meta_id,meta_bgn,meta_end)
### end of lbc --------------------------------------------------------

### begin of da --------------------------------------------------------
def da(xmlFile, expdir):
  task_id='da'
  cycledefs='prod'
  # Task-specific EnVars beyond the task_common_vars
  dcTaskEnv={
    '_PLACEHOLDER_': 'just a place holder',
  }
  # dependencies
  hrs=os.getenv('PROD_BGN_AT_HRS', '3 15')
  hrs=hrs.split(' ')
  streqs=""; strneqs=""; first=True
  for hr in hrs:
    hr=f"{hr:0>2}"
    if first:
      first=False
      streqs=streqs  +f"          <streq><left><cyclestr>@H</cyclestr></left><right>{hr}</right></streq>"
      strneqs=strneqs+f"          <strneq><left><cyclestr>@H</cyclestr></left><right>{hr}</right></strneq>"
    else:
      streqs=streqs  +f"\n          <streq><left><cyclestr>@H</cyclestr></left><right>{hr}</right></streq>"
      strneqs=strneqs+f"\n          <strneq><left><cyclestr>@H</cyclestr></left><right>{hr}</right></strneq>"

  timedep=""
  realtime=os.getenv("REALTIME","false")
  starttime=get_cascade_env(f"STARTTIME_{task_id}".upper())
  if realtime.upper() == "TRUE":
    timedep=f'\n    <timedep><cyclestr offset="{starttime}">@Y@m@d@H@M00</cyclestr></timedep>'
  #
  DATAROOT=os.getenv("DATAROOT","DATAROOT_NOT_DEFINED")
  RUN='rrfs'
  NET=os.getenv("NET","NET_NOT_DEFINED")
  VERSION=os.getenv("VERSION","VERSION_NOT_DEFINED")
  dependencies=f'''
  <dependency>
  <and>{timedep}
    <or>
      <and>
        <or>
{streqs}
        </or>
        <taskdep task="ic"/>
      </and>
      <and>
        <or>
{strneqs}
        </or>
        <datadep age="00:05:00"><cyclestr offset="-1:00:00">{DATAROOT}/{NET}/{VERSION}/{RUN}.@Y@m@d/@H/fcst/</cyclestr><cyclestr>restart.@Y-@m-@d_@H.@M.@S.nc</cyclestr></datadep>
      </and>
    </or>
  </and>
  </dependency>'''
  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies)
### end of da --------------------------------------------------------

### begin of fcst --------------------------------------------------------
def fcst(xmlFile, expdir):
  task_id='fcst'
  cycledefs='prod'
  # Task-specific EnVars beyond the task_common_vars
  dcTaskEnv={
    '_PLACEHOLDER_': 'just a place holder',
  }
  # dependencies
  hrs=os.getenv('PROD_BGN_AT_HRS', '3 15')
  hrs=hrs.split(' ')
  streqs=""; strneqs=""; first=True
  for hr in hrs:
    hr=f"{hr:0>2}"
    if first:
      first=False
      streqs=streqs  +f"        <streq><left><cyclestr>@H</cyclestr></left><right>{hr}</right></streq>"
      strneqs=strneqs+f"        <strneq><left><cyclestr>@H</cyclestr></left><right>{hr}</right></strneq>"
    else:
      streqs=streqs  +f"\n        <streq><left><cyclestr>@H</cyclestr></left><right>{hr}</right></streq>"
      strneqs=strneqs+f"\n        <strneq><left><cyclestr>@H</cyclestr></left><right>{hr}</right></strneq>"

  timedep=""
  realtime=os.getenv("REALTIME","false")
  starttime=get_cascade_env(f"STARTTIME_{task_id}".upper())
  if realtime.upper() == "TRUE":
    timedep=f'\n   <timedep><cyclestr offset="{starttime}">@Y@m@d@H@M00</cyclestr></timedep>'
  #
  DATAROOT=os.getenv("DATAROOT","DATAROOT_NOT_DEFINED")
  RUN='rrfs'
  NET=os.getenv("NET","NET_NOT_DEFINED")
  VERSION=os.getenv("VERSION","VERSION_NOT_DEFINED")
  dependencies=f'''
  <dependency>
  <and>{timedep}
   <or>
    <metataskdep metatask="lbc" cycle_offset="0:00:00"/>
    <metataskdep metatask="lbc" cycle_offset="-1:00:00"/>
    <metataskdep metatask="lbc" cycle_offset="-2:00:00"/>
    <metataskdep metatask="lbc" cycle_offset="-3:00:00"/>
    <metataskdep metatask="lbc" cycle_offset="-4:00:00"/>
    <metataskdep metatask="lbc" cycle_offset="-5:00:00"/>
    <metataskdep metatask="lbc" cycle_offset="-6:00:00"/>
   </or>
   <or>
    <and>
      <or>
{streqs}
      </or>
      <taskdep task="ic"/>
    </and>
    <and>
      <and>
{strneqs}
      </and>
      <taskdep task="da"/>
    </and>
   </or>
  </and>
  </dependency>'''
  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies)
### end of fcst --------------------------------------------------------
