#!/usr/bin/env bash
export PS4="+ $(basename ${BASH_SOURCE})[${LINENO}]:"
set -x
date
echo "This is a dummy task!"
exit 0
