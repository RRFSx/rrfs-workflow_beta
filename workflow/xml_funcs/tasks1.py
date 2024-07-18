#!/usr/bin/env python
import os
from xml_funcs.base import xml_task, source

### begin of ic --------------------------------------------------------
def ic(xmlFile, expdir):
  task_id='ic'
  cycledefs='ic'
  # Task-specific EnVars beyond the task_common_vars
  dcTaskEnv={
    '_PLACEHOLDER_': 'just a place holder',
  }
  # dependencies
  source(f'{expdir}/config/config.{task_id}')
  prefix=os.getenv('IC_PREFIX','GFS')
  offset=os.getenv('IC_OFFSET_HRS','3')
  COMINgfs=os.getenv("COMINgfs",'COMINgfs_not_defined')
  COMINrrfs=os.getenv("COMINrrfs",'COMINrrfs_not_defined')
  COMINrap=os.getenv("COMINrap",'COMINrap_not_defined')
  COMINhrrr=os.getenv("COMINhrrr",'COMINhrrr_not_defined')
  COMINgefs=os.getenv("COMINgefs",'COMINgefs_not_defined')
  if prefix == "GFS":
    fpath=f'{COMINgfs}/gfs.@Y@m@d/@H/gfs.t@Hz.pgrb2.0p25.f{offset:>03}'
  elif prefix == "RRFS":
    fpath=f'{COMINrrfs}/rrfs.@Y@m@d/@H/rrfs.t@Hz.pgrb2.0p25.f{offset:>03}'
  elif prefix == "RAP":
    fpath=f'{COMINrap}/rap.@Y@m@d/@H/rap.t@Hz.pgrb2.0p25.f{offset:>03}'
  elif prefix == "HRRR":
    fpath=f'{COMINhrrr}/hrrr.@Y@m@d/@H/hrrr.t@Hz.pgrb2.0p25.f{offset:>03}'
  elif prefix == "GEFS":
    fpath=f'{COMINgefs}/gefs.@Y@m@d/@H/gefs.t@Hz.pgrb2.0p25.f{offset:>03}'
  else:
    fpath=f'/not_supported_IC_PREFIX'

  dependencies=f'''
  <dependency>
  <datadep age="00:05:00"><cyclestr offset="-{offset}:00:00">{fpath}</cyclestr></datadep>
  </dependency>'''
  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies)
### end of ic --------------------------------------------------------

### begin of lbc --------------------------------------------------------
def lbc(xmlFile, expdir):
  task_id='lbc'
  cycledefs='lbc'
  # Task-specific EnVars beyond the task_common_vars
  dcTaskEnv={
    '_PLACEHOLDER_': 'just a place holder',
  }
  # dependencies
  source(f'{expdir}/config/config.{task_id}')
  prefix=os.getenv('LBC_PREFIX','GFS')
  offset=int(os.getenv('LBC_OFFSET_HRS','6'))
  length=int(os.getenv('LBC_LENGTH_HRS','18'))
  interval=int(os.getenv('LBC_INTERVAL_HRS','3'))
  COMINgfs=os.getenv("COMINgfs",'COMINgfs_not_defined')
  COMINrrfs=os.getenv("COMINrrfs",'COMINrrfs_not_defined')
  COMINrap=os.getenv("COMINrap",'COMINrap_not_defined')
  COMINhrrr=os.getenv("COMINhrrr",'COMINhrrr_not_defined')
  COMINgefs=os.getenv("COMINgefs",'COMINgefs_not_defined')
  if prefix == "GFS":
    fpath=f'{COMINgfs}/gfs.@Y@m@d/@H/gfs.t@Hz.pgrb2.0p25'
  elif prefix == "RRFS":
    fpath=f'{COMINrrfs}/rrfs.@Y@m@d/@H/rrfs.t@Hz.pgrb2.0p25'
  elif prefix == "RAP":
    fpath=f'{COMINrap}/rap.@Y@m@d/@H/rap.t@Hz.pgrb2.0p25'
  elif prefix == "HRRR":
    fpath=f'{COMINhrrr}/hrrr.@Y@m@d/@H/hrrr.t@Hz.pgrb2.0p25'
  elif prefix == "GEFS":
    fpath=f'{COMINgefs}/gefs.@Y@m@d/@H/gefs.t@Hz.pgrb2.0p25'
  else:
    fpath=f'/not_supported_LBC_PREFIX'

  datadep=""; first=True
  for fhr in range(offset,offset+length+interval,interval):
    if first:
      first=False
      datadep=datadep+f'    <datadep age="00:05:00"><cyclestr offset="-{offset}:00:00">{fpath}.f{fhr:>03}</cyclestr></datadep>'
    else:
      datadep=datadep+f'\n    <datadep age="00:05:00"><cyclestr offset="-{offset}:00:00">{fpath}.f{fhr:>03}</cyclestr></datadep>'

  dependencies=f'''
  <dependency>
  <and>
{datadep}
  </and>
  </dependency>'''
  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies)
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
  hrs=os.getenv('PROD_BGN_HRS', '3 15')
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

  dependencies=f'''
  <dependency>
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
      <taskdep task="fcst" cycle_offset="-1:00:00"/>
    </and>
  </or>
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
  hrs=os.getenv('PROD_BGN_HRS', '3 15')
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

  dependencies=f'''
  <dependency>
  <and>
   <or>
    <taskdep task="lbc" cycle_offset="0:00:00"/>
    <taskdep task="lbc" cycle_offset="-1:00:00"/>
    <taskdep task="lbc" cycle_offset="-2:00:00"/>
    <taskdep task="lbc" cycle_offset="-3:00:00"/>
    <taskdep task="lbc" cycle_offset="-4:00:00"/>
    <taskdep task="lbc" cycle_offset="-5:00:00"/>
    <taskdep task="lbc" cycle_offset="-6:00:00"/>
   </or>
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
      <taskdep task="da"/>
    </and>
   </or>
  </and>
  </dependency>'''
  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies)
### end of fcst --------------------------------------------------------
