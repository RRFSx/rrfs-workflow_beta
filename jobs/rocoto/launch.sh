#!/usr/bin/env bash
# load modules for the rocoto workflow manager
#
set +x # supress messy output in the module load process
source /etc/profile
source ${EXPDIR}/exp.setup
module purge
module use ${HOMErrfs}/sorc/RDASApp/modulefiles
module load RDAS/${MACHINE}.intel
module list
set -x
#
COMMAND=$1  #get the JJOB name
task_id=${COMMAND#*_}
export task_id=${task_id,,} #to lower case
export rrfs_ver=${VERSION}
# tweaks for non-NCO runs
export cpreq="ln -snf" #use soft link instead of copy for non-NCO experiments
export COMOUT="${COMROOT}/${NET}/${rrfs_ver}/${RUN}.${PDY}/${cyc}" # task_id not included as compath.py may not be able to find this subdirectory
export DATA=${DATAROOT}/${NET}/${rrfs_ver}/${RUN}.${PDY}/${cyc}/${task_id}
export COMINrrfs="${COMROOT}/${NET}/${rrfs_ver}" # we may need to use data from previous cycles
export NTASKS=${SLURM_NTASKS}
#
${HOMErrfs}/jobs/${COMMAND}
