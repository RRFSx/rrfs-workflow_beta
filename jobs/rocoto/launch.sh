#!/usr/bin/env bash
# load modules for the rocoto workflow manager
# This script will NOT be needed by NCO
#
declare -rx PS4='+ $(basename ${BASH_SOURCE[0]:-${FUNCNAME[0]:-"Unknown"}})[${LINENO}]${id}: '
set +x # supress messy output in the module load process
source /etc/profile
source ${EXPDIR}/exp.setup
module purge
module use ${HOMErrfs}/sorc/RDASApp/modulefiles
module load RDAS/${MACHINE}.intel
module list
set -x
#
# tweaks for non-NCO runs
COMMAND=$1  #get the JJOB name
task_id=${COMMAND#*_}
export task_id=${task_id,,} #to lower case
export rrfs_ver=${VERSION}
if [[ -z "${ENS_INDEX}" ]]; then
  RUN='rrfs'
  export DATA=${DATAROOT}/${NET}/${rrfs_ver}/${RUN}.${PDY}/${cyc}/${task_id}
else
  RUN='ens'
  if [[ "${task_id}" == "ens_da"  ]]; then
    export DATA=${DATAROOT}/${NET}/${rrfs_ver}/${RUN}.${PDY}/${cyc}/${task_id}
  else
    export DATA=${DATAROOT}/${NET}/${rrfs_ver}/${RUN}.${PDY}/${cyc}/mem${ENS_INDEX}/${task_id}
  fi
fi
export cpreq="ln -snf" #use soft link instead of copy for non-NCO experiments
export COMOUT="${COMROOT}/${NET}/${rrfs_ver}/${RUN}.${PDY}/${cyc}" # task_id not included as compath.py may not be able to find this subdirectory
export COMINrrfs="${COMROOT}/${NET}/${rrfs_ver}" # we may need to use data from previous cycles
export NTASKS=${SLURM_NTASKS}
#
case ${task_id} in
  clean|graphics|dummy)
    ${HOMErrfs}/jobs/rocoto/${task_id}.sh
    ;;
  *)
   ${HOMErrfs}/jobs/${COMMAND}
   ;;
esac
