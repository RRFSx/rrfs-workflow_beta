#!/usr/bin/env python
import os
from datetime import datetime, timedelta
from xml_funcs.base import source
0
def smart_cycledefs(realtime,realtime_days,retro_period):
  if realtime.upper() == "TRUE":
    now=datetime.now()
    end=now+timedelta(days=int(realtime_days))
    pdy=now.strftime("%Y%m%d")
    pdy2=end.strftime("%Y%m%d")
    hr_bgn=now.hour
    hr_end='23'
  else:
    retrodates=retro_period.split("-")
    pdy=retrodates[0][:8]
    hr_bgn=retrodates[0][8:]
    pdy2=retrodates[1][:8]
    hr_end=retrodates[1][8:]
  #
  if int(hr_bgn) <= 3:
    ic_bgn='03'
    lbc_bgn='00'
  else:
    ic_bgn='15'
    lbc_bgn='12'
  text=f'\
export CYCLEDEF_IC="{pdy}{ic_bgn}00 {pdy2}{hr_end}00 12:00:00"\n\
export CYCLEDEF_LBC="{pdy}{lbc_bgn}00 {pdy2}{hr_end}00 06:00:00"\n\
export CYCLEDEF_PROD="{pdy}{ic_bgn}00 {pdy2}{hr_end}00 01:00:00"\n\
'
  return text
#export CYCLEDEF_PROD="00 00-23 26,27 05 2024 *"\n\
