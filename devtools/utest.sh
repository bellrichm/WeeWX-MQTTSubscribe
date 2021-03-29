#! /bin/bash
if [ -z "$1" ]
then
    exit 4
else
    TEST=$1
fi

export PYENV_VERSION=2.7.17
export WEEWX=weewx4
echo "Running python $PYENV_VERSION $WEEWX"
PYTHONPATH=bin:../$WEEWX/bin python bin/user/tests/unit/$TEST

export PYENV_VERSION=3.6.9
export WEEWX=weewx4
echo "Running python $PYENV_VERSION $WEEWX"
PYTHONPATH=bin:../$WEEWX/bin python bin/user/tests/unit/$TEST

export PYENV_VERSION=3.5.9
export WEEWX=weewx4
echo "Running python $PYENV_VERSION $WEEWX"
PYTHONPATH=bin:../$WEEWX/bin python bin/user/tests/unit/$TEST

export PYENV_VERSION=2.7.17
export WEEWX=weewx3
echo "Running python $PYENV_VERSION $WEEWX"
PYTHONPATH=bin:../$WEEWX/bin python bin/user/tests/unit/$TEST
