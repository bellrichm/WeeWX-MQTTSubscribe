#! /bin/bash
#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
if [ -z "$1" ]
then
    exit 4
else
    TEST=$1
fi

source ./devtools/python_versions.sh

for version in ${weewx4_python_versions[@]}; do
    export PYENV_VERSION=$version
    export WEEWX=weewx4
    echo "Running python $PYENV_VERSION $WEEWX"
    PYTHONPATH=bin:../$WEEWX/bin python bin/user/tests/integ/$TEST
done

for version in ${weewx3_python_versions[@]}; do
    export PYENV_VERSION=$version
    export WEEWX=weewx3
    echo "Running python $PYENV_VERSION $WEEWX"
    PYTHONPATH=bin:../$WEEWX/bin python bin/user/tests/integ/$TEST
done
