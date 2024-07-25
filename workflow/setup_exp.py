#!/usr/bin/env python
# Aloha!
#
import os, sys, shutil, glob
from xml_funcs.base import source, get_yes_or_no
from xml_funcs.smart_cycledefs import smart_cycledefs
from xml_funcs.setup_xml import setup_xml
print(f'\nAloha!')

if len(sys.argv) == 2:
  EXPin = sys.argv[1]
else:
  EXPin = "exp.setup"

# find the HOMErrfs directory
HOMErrfs=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.system(f'{HOMErrfs}/ush/init.sh')
#
if os.path.exists(EXPin):
  source(EXPin)
else:
  print(f'{EXPin}: no such file')
  exit()
user_id=os.getlogin()
# create comroot (no matter exists or not)
comroot=os.getenv('COMROOT',f'/tmp/${user_id}/com')
dataroot=os.getenv('DATAROOT',f'/tmp/${user_id}/stmp')
os.makedirs(comroot,exist_ok=True)
os.makedirs(dataroot,exist_ok=True)

# set the expdir variable
basedir=os.getenv('EXP_BASEDIR',f'/tmp/{user_id}')
version=os.getenv('VERSION','community')
exp_name=os.getenv('EXP_NAME','')
expdir=f'{basedir}/{version}'
if exp_name !="":
  expdir=f'{expdir}/{exp_name}'

# if expdir exists, find an available dir name to backup old files first
# and then upgrade expdir
if os.path.exists(expdir):
  knt=1
  savedir=f'{expdir}_old{knt:04}'
  while os.path.exists(savedir):
    knt += 1
    savedir=f'{expdir}_old{knt:04}'
  shutil.copytree(expdir, savedir, copy_function=shutil.copy2)
else:
  os.makedirs(expdir)

# copy the default config first and then sub to substitute the default one
configdir=f'{HOMErrfs}/workflow/config'
exp_configdir=f'{expdir}/config'
if os.path.exists(exp_configdir):
  if os.path.isfile(exp_configdir):
    os.remove(exp_configdir)
  else:
    shutil.rmtree(exp_configdir)
shutil.copytree(configdir,exp_configdir)

# generate cycledefs
# the goal is to create cycledefs smartly
realtime=os.getenv('REALTIME','false')
realtime_days=os.getenv('REALTIME_DAYS','60')
retro_period=os.getenv('RETRO_PERIOD','2024070200-2024071200')
smart_cycledefs_text=smart_cycledefs(realtime,realtime_days,retro_period)

# generate exp.setup under $expdir
source(f'{HOMErrfs}/ush/detect_machine.sh')
machine=os.getenv('MACHINE')
if machine=='UNKNOWN':
    print(f'WARNING: machine is UNKNOWN! ')
text=f'''#=== auto-generation of HOMErrfs, MACHINE, EXPDIR, CYCLEDEF_*
export HOMErrfs={HOMErrfs}
export MACHINE={machine}
export EXPDIR={expdir}
'''
#
text=text+f'{smart_cycledefs_text}#\n'
EXPout=f'{expdir}/exp.setup'
with open(EXPin, 'r') as infile, open(EXPout, 'w') as outfile:
  # add HOMErrfs, MACHINE, EXPDIR, CYCLEDEF_* to the beginning of the exp.setup file under expdir/
  header=""
  still_header=True
  for line in infile:
    if still_header:
      if line.strip().startswith('#'):
        header=header+line
      else:
        still_header=False
        outfile.write(header)
        outfile.write(text)
        outfile.write(line)
    else:
      rm_list=('EXP_BASEDIR=','EXP_NAME=','REALTIME=','REALTIME_DAYS=','RETRO_PERIOD=','RETRO_CYCLETHROTTLE=',
        'RETRO_TASKTHROTTLE=','ACCOUNT','QUEUE','PARTITION','RESERVATION','STARTTIME','NODES','WALLTIME'
          )
      found=False
      for rmstr in rm_list:
        if rmstr in line:
          found=True; break
      if not found:
        outfile.write(line)

setup_xml(expdir) 
#
# end of setup_exp.py
