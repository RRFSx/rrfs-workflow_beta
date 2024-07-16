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
  dependencies=""

  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies)
### end of fcst --------------------------------------------------------
