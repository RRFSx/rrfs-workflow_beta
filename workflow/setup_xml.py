#!/usr/bin/env python
#
import os, sys, stat
from xml_funcs.base import header_begin, header_entities, header_end, source, \
  wflow_begin, wflow_log, wflow_cycledefs, wflow_end, get_cascade_env
from xml_funcs.tasks1 import ic, lbc, da, fcst

### setup_xml
def setup_xml(expdir):
  # source the config cascade
  source(f'{expdir}/exp.setup')
  source(f"{expdir}/config/config.base")
  machine=os.getenv('MACHINE').lower()
  source(f"{expdir}/config/config.{machine}")
  #
  dcCycledef={}
  dcCycledef['ic']=os.getenv('CYCLEDEF_IC')
  dcCycledef['lbc']=os.getenv('CYCLEDEF_LBC')
  #dcCycledef['spinup']=os.getenv('CYCLEDEF_SPINUP')
  dcCycledef['prod']=os.getenv('CYCLEDEF_PROD') #gge.debug
  
  COMROOT=os.getenv('COMROOT','COMROOT_not_defined')
  TAG=os.getenv('TAG','TAG_not_defined')
  NET=os.getenv('NET','NET_not_defined')
  VERSION=os.getenv('VERSION','VERSION_not_defined')

  fPath=f"{expdir}/rrfs.xml"
  with open(fPath, 'w') as xmlFile:
    header_begin(xmlFile)
    header_entities(xmlFile,expdir)
    header_end(xmlFile)
    wflow_begin(xmlFile)
    log_fpath=f'{COMROOT}/{NET}/{VERSION}/logs/rrfs.@Y@m@d/@H/rrfs_{TAG}.log'
    wflow_log(xmlFile,log_fpath)
    wflow_cycledefs(xmlFile,dcCycledef)
    
    #tasks
    ic(xmlFile,expdir)
    lbc(xmlFile,expdir)
    da(xmlFile,expdir)
    fcst(xmlFile,expdir)
  
    wflow_end(xmlFile)

  fPath=f"{expdir}/run_rocoto.sh"
  with open(fPath,'w') as rocotoFile:
    text=f'''
#!/usr/bin/env bash
source /etc/profile
module load rocoto
cd {expdir}
rocotorun -w rrfs.xml -d rrfs.db
'''
    rocotoFile.write(text)

  # set run_rocoto.sh to be executable
  st = os.stat(fPath)
  os.chmod(fPath, st.st_mode | stat.S_IEXEC)

  print(f'rrfs.xml and run_rocoto.sh has been created at:\n  {expdir}')
### end of setup_xml

### run setup_xml.py from the command line
if __name__ == "__main__":
  # get the expdir from the command line
  if len(sys.argv) != 2:
    print("Usage: setup_xml.py expdir")
    sys.exit(1)
  
  # Retrieve arguments - the path to the exp_setting file
  expdir = sys.argv[1]

  setup_xml(expdir)
