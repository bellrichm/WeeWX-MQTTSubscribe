#! /bin/bash
#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#   
source ./devtools/python_versions.sh

if [ -z "$1" ]; then
    exit 4
elif [ -z "$2" ]; then
    WEEWX_VERSION=$weewx_default_version
    PY_VERSION=$weewx_default_python_version
    TEST=$1
elif [ -z "$3" ]; then
    WEEWX_VERSION=$weewx_default_version
    PY_VERSION=$1
    TEST=$2
else
    WEEWX_VERSION=$1
    PY_VERSION=$2
    TEST=$3
fi

export PYENV_VERSION=$PY_VERSION
export WEEWX=$WEEWX_VERSION
echo "Running python $PY_VERSION $WEEWX_VERSION"
PYTHONPATH=bin:../$WEEWX_VERSION/bin pytest bin/user/tests/unit/$TEST
date