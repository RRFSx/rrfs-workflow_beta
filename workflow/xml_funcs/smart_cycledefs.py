#!/usr/bin/env python
import os
from xml_funcs.base import source, get_cascade_env

def smart_cycledefs(realtime,reatime_length,retro_period):
  text='''
\n\
export CYCLEDEF_IC="202405270300 202405270500 12:00:00"\n\
export CYCLEDEF_LBC="202405270000 202405270100 06:00:00"\n\
export CYCLEDEF_SPINUP="00 03-08,15-20 26,27 05 2024 *"\n\
export CYCLEDEF_PROD="202405270300 202405270500 01:00:00"\n\
export CYCLEDEF_PROD_LONG='00 00,12 26 05 2024 *'
'''
  return text
#export CYCLEDEF_PROD="00 00-23 26,27 05 2024 *"\n\
