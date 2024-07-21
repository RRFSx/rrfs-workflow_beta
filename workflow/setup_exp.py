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
os.system(f'{HOMErrfs}/ush/init.sh')
#
source(fpath)
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
os.makedirs(exp_configdir,exist_ok=True)
for cfile in glob.glob(f'{configdir}/config.*'):
  shutil.copy(cfile,exp_configdir)
#
sub=os.getenv("CONFIG_SUB","")
if sub != "":
  subdir=f'{configdir}/{sub}'
  if os.path.isdir(subdir):
    for subfile in glob.glob(f'{subdir}/*'):
      shutil.copy(subfile,exp_configdir)
  else:
    print(f'"subdir" does not exist')

# generate cycledefs
# the goal is to create cycledefs smartly
# 
realtime=os.getenv('REALTIME','false')
realtime_days=os.getenv('REALTIME_DAYS','60')
retro_period=os.getenv('RETRO_PERIOD','2024070200-2024071200')
smart_cycledefs_text=smart_cycledefs(realtime,realtime_days,retro_period)

# generate exp.setup under $expdir
source(f'{HOMErrfs}/ush/detect_machine.sh')
machine=os.getenv('MACHINE')
if machine=='UNKNOWN':
    print(f'WARNING: machine is UNKNOWN! ')
tag=os.getenv('TAG','rrfs')
net=os.getenv('NET','rrfs')
run=os.getenv('RUN','rrfs')
physics_suite=os.getenv('PHYSICS_SUITE','PHYSICS_SUITE_NOT_DEFINED')
retro_cyclethrottle=os.getenv('RETRO_CYCLETHROTTLE','6')
retro_taskthrottle=os.getenv('RETRO_TASKTHROTTLE','100')
text=f'''#!/usr/bin/env bash
export EXPDIR={expdir}
export COMROOT={comroot}
export DATAROOT={dataroot}
export HOMErrfs={HOMErrfs}
export VERSION={version}
export MACHINE={machine}
export NET={net}
export RUN={run}
export TAG={tag}
export PHYSICS_SUITE={physics_suite}
export REALTIME={realtime}
'''
#
if realtime.upper() == "FALSE": 
  text=text+f'\
export RETRO_CYCLETHROTTLE={retro_cyclethrottle}\n\
export RETRO_TASKTHROTTLE={retro_taskthrottle}\n\
'
#
text=text+f'{smart_cycledefs_text}\n'
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
  print(f'when you complete fine-tuning configurations, run\n  ./setup_xml.py {expdir}\nto generate an xml file for rocoto')
#
# end of setup_exp.py
