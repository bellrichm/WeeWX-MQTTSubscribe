#! /bin/bash
#    Copyright (c) 2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
source ./devtools/python_versions.sh

# Note, the value for $WEEWX can be relative. For example ../weewx-source/weewx-3.7.1
if [ -z "$1" ]; then
    WEEWX=weewx5
else
    WEEWX=$1
fi

if [ -z "$2" ]; then
    export PYENV_VERSION=$weewx_default_python_version    
else
    export PYENV_VERSION=$2
fi

python_command='python'$PYENV_VERSION
python_version=$(pyenv which $python_command)
echo "Running $python_version $WEEWX"

PYTHONPATH=bin:../$WEEWX/src:../$WEEWX/bin pytest bin/user/tests/e2e
date