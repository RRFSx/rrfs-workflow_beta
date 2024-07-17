#!/usr/bin/env python
import os
from xml_funcs.base import xml_task

### begin of ic --------------------------------------------------------
def ic(xmlFile, expdir):
  task_id='ic'
  cycledefs='ic'
  # Task-specific EnVars beyond the task_common_vars
  dcTaskEnv={
    '_PLACEHOLDER_': 'just a place holder',
  }
  # dependencies
  dependencies=""

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
  dependencies=""

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
  dependencies=""

  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies)
### end of da --------------------------------------------------------

### begin of fcst --------------------------------------------------------
def fcst(xmlFile, expdir):
  task_id='fcst'
  cycledefs='spinup,prod'
  # Task-specific EnVars beyond the task_common_vars
  dcTaskEnv={
    '_PLACEHOLDER_': 'just a place holder',
  }
  # dependencies
  offset=3
  hrs=os.getenv('PROD_BGN_HRS', '3 5')
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
      <taskdep task="lbc" cycle_offset="-{offset}:00:00"/>
    </and>
    <and>
      <or>
{strneqs}
      </or>
      <taskdep task="lbc" cycle_offset="-{offset}:00:00"/>
      <taskdep task="da"/>
    </and>
  </or>
  </dependency>'''

  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies)
### end of fcst --------------------------------------------------------
