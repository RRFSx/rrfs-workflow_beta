#!/usr/bin/env bash
#
# FIX_RRFS locaitons at different HPC platforms
#
rundir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source ${rundir}/detect_machine.sh

case ${MACHINE} in
  hera)
    FIX_RRFS_LOCATION=/scratch2/BMC/rtrr/FIX_RRFS2
    ;;
  jet)
    FIX_RRFS_LOCATION=/lfs5/BMC/nrtrr/FIX_RRFS2
    ;;
  orion|hercules)
    FIX_RRFS_LOCATION=/work/noaa/rtrr/FIX_RRFS2
    ;;
  *)
    FIX_RRFS_LOCATION=/unknown/location
    echo "platform not supported: ${MACHINE}"
    ;;
esac
