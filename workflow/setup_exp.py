#!/usr/bin/env python
# Aloha!
#
import os, sys, shutil, glob
from xml_funcs.base import source, get_yes_or_no
from xml_funcs.smart_cycledefs import smart_cycledefs
from setup_xml import setup_xml

if len(sys.argv) != 2:
  print("Usage: setup_exp.py exp_setting")
  sys.exit(1)

# Retrieve arguments - the path to the exp_setting file
fpath = sys.argv[1]

# find the HOMErrfs directory
HOMErrfs=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# create a dcionary for all EXP settings
user_id=os.getlogin()
dcExp={  #default vaules for some variables
  'exp_basedir': f'/tmp/{user_id}',
  'comroot': f'/tmp/${user_id}/ptmp',
  'dataroot': f'/tmp/${user_id}/stmp',
  'version': 'community',
  'exp_name': '',
  'config_sample': 'default',
  'realtime': False,
  'retro_period': '2024070200-2024071200'
}
for line in open(fpath): #read exp_setting
  sline=line.strip()
  if (not sline.startswith("#")) and ("=" in sline):
    key,value=sline.strip().split("=",1)
    if "#" in value:
      value,comment=value.split("#",1)
    dcExp[key.strip().strip('"').strip("'")]=value.strip().strip('"').strip("'")

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

# copy config_default first and then files from the selected config_sample
config_sample=dcExp['config_sample']
config_default=f'{HOMErrfs}/workflow/samples/config_default'
configdir=f'{HOMErrfs}/workflow/samples/config_{config_sample}'
exp_configdir=f'{expdir}/config'
if os.path.exists(exp_configdir):
  shutil.rmtree(exp_configdir)
if config_sample!="default": #copy default first if a non_default sample is selected
  shutil.copytree(config_default,exp_configdir)
for file in glob.glob(f'{configdir}/*'): #overwrite default config files using the selected sample
  shutil.copy(file,exp_configdir)

# generate cycledefs
# the goal is to create cycledefs smartly
# 
realtime=dcExp['realtime']
realtime_length=dcExp['realtime_length']
retro_period=dcExp['retro_period']
smart_cycledefs_text=smart_cycledefs(realtime,realtime_length,retro_period)

# generate an alternate version of exp_setting for workflow setup
source(f'{HOMErrfs}/ush/detect_machine.sh')
machine=os.getenv('MACHINE')
if machine=='UNKNOWN':
    print(f'WARNING: machine is UNKNOWN! ')
tag=dcExp['tag']
net=dcExp['net']
run=dcExp['run']
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
export REALTIME_LENGTH={realtime_length}\n\
export RETRO_PERIOD={retro_period}\n\
{smart_cycledefs_text}\n\
#\n\
# for reference purpose only\n\
#config_sample={config_sample}\n\
'
fpath=f'{expdir}/config.exp'
with open(fpath, 'w') as file:
  file.write(text)

# print out information for users
print(f'\
Aloha!\n\n\
Based on the "{config_sample}" config sample,expdir created at:\n\
  {expdir}\n\
We can now create an rocoto xml file if no intention to further fine-tune configurations, \n\
Or we can exit this program, fine-tune configurations under expdir, and then run "set_xml.py expdir" to create an xml file')
response=get_yes_or_no('Do you want to create an xml file right now(y/n):\n')
if response in ['yes', 'y']:
  setup_xml(expdir) 
#
# end of setup_exp.py
