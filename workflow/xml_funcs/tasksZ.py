#!/usr/bin/env python
# this file hosts all tasks that will not be needed by NCO
import os
from xml_funcs.base import xml_task, source, get_cascade_env

### begin of clean --------------------------------------------------------
def clean(xmlFile, expdir):
  task_id='clean'
  cycledefs='prod'
  # Task-specific EnVars beyond the task_common_vars
  dcTaskEnv={
    '_PLACEHOLDER_': 'This is a non-NCO task that will not needed in operation'
  }
  # dependencies
  dependencies=""
  #
  xml_task(xmlFile,expdir,task_id,cycledefs,dcTaskEnv,dependencies)
### end of clean --------------------------------------------------------
