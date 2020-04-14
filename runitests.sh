#! /bin/bash

export PYENV_VERSION=2.7.17
export WEEWX=weewx4
echo "Running python $PYENV_VERSION $WEEWX"
PYTHONPATH=bin:../$WEEWX/bin python -m unittest discover bin/user/tests/func

export PYENV_VERSION=3.6.9
export WEEWX=weewx4
echo "Running python $PYENV_VERSION $WEEWX"
PYTHONPATH=bin:../$WEEWX/bin python -m unittest discover bin/user/tests/func

export PYENV_VERSION=3.5.9
export WEEWX=weewx4
echo "Running python $PYENV_VERSION $WEEWX"
PYTHONPATH=bin:../$WEEWX/bin python -m unittest discover bin/user/tests/func

PYENV_VERSION=2.7.17
export WEEWX=weewx3
echo "Running python $PYENV_VERSION $WEEWX"
PYTHONPATH=bin:../$WEEWX/bin python -m unittest discover bin/user/tests/func

