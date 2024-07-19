#!/usr/bin/env python
# Aloha!
#
import os, sys, shutil, glob
from xml_funcs.base import source, get_yes_or_no
from xml_funcs.smart_cycledefs import smart_cycledefs
from setup_xml import setup_xml

if len(sys.argv) != 2:
  print("Usage: setup_exp.py exp.setup")
  sys.exit(1)

# Retrieve arguments - path to exp.setup
fpath = sys.argv[1]

# find the HOMErrfs directory
HOMErrfs=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# create a dcionary for all EXP settings
user_id=os.getlogin()
source(fpath)
dcExp={
  'exp_basedir': os.getenv('EXP_BASEDIR',f'/tmp/{user_id}'),
  'comroot': os.getenv('COMROOT',f'/tmp/${user_id}/com'),
  'dataroot': os.getenv('DATAROOT',f'/tmp/${user_id}/stmp'),
  'version': os.getenv('VERSION','community'),
  'net': os.getenv('NET','rrfs'),
  'run': os.getenv('RUN','rrfs'),
  'exp_name': os.getenv('EXP_NAME',''),
  'tag': os.getenv('TAG','rrfs'),
  'realtime': os.getenv('REALTIME','false'),
  'realtime_days': os.getenv('REALTIME_DAYS','60'),
  'retro_period': os.getenv('RETRO_PERIOD','2024070200-2024071200'),
  'retro_cyclethrottle': os.getenv('RETRO_CYCLETHROTTLE','5'),
  'retro_taskthrottle': os.getenv('RETRO_TASKTHROTTLE','100')
}

# create comroot (no matter exists or not)
comroot=dcExp['comroot']
dataroot=dcExp['dataroot']
os.makedirs(comroot,exist_ok=True)
os.makedirs(dataroot,exist_ok=True)

# set the expdir variable
basedir=dcExp["exp_basedir"]
version=dcExp["version"]
exp_name=dcExp["exp_name"]
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

# copy the config directory
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
# 
realtime=dcExp['realtime']
realtime_days=dcExp['realtime_days']
retro_period=dcExp['retro_period']
_period=dcExp['retro_period']
smart_cycledefs_text=smart_cycledefs(realtime,realtime_days,retro_period)

# generate exp.setup under $expdir
source(f'{HOMErrfs}/ush/detect_machine.sh')
machine=os.getenv('MACHINE')
if machine=='UNKNOWN':
    print(f'WARNING: machine is UNKNOWN! ')
tag=dcExp['tag']
net=dcExp['net']
run=dcExp['run']
retro_cyclethrottle=dcExp['retro_cyclethrottle']
retro_taskthrottle=dcExp['retro_taskthrottle']
text=f'#!/usr/bin/env bash\n\
export EXPDIR={expdir}\n\
export COMROOT={comroot}\n\
export DATAROOT={dataroot}\n\
export HOMErrfs={HOMErrfs}\n\
export VERSION={version}\n\
export MACHINE={machine}\n\
export NET={net}\n\
export RUN={run}\n\
export TAG={tag}\n\
export REALTIME={realtime}\n\
export REALTIME_DAYS={realtime_days}\n\
export RETRO_PERIOD={retro_period}\n\
export RETRO_CYCLETHROTTLE={retro_cyclethrottle}\n\
export RETRO_TASKTHROTTLE={retro_taskthrottle}\n\
{smart_cycledefs_text}\n\
'
fpath=f'{expdir}/exp.setup'
with open(fpath, 'w') as file:
  file.write(text)

# print out information for users
print(f'\
Aloha!\n\
expdir created at:\n\
  {expdir}\n\
We can now create an rocoto xml file if no intention to further fine-tune configurations, \n\
Or we can exit this program, fine-tune configurations under expdir, and then run "set_xml.py expdir" to create an xml file')
response=get_yes_or_no('Do you want to create an xml file right now(y/n):\n')
if response in ['yes', 'y']:
  setup_xml(expdir) 
else:
  print(f'when you complete fine-tuning configurations, run\n  ./setup.xml.py {expdir}\nto generate an xml file for rocoto')
#
# end of setup_exp.py
