#! /bin/bash
if [ -z "$1" ]
then
    WEEWX=weewx
else
    WEEWX=$1
fi

if [ -z "$2" ]
then
    PYTHON=python2
else
    PYTHON=$2
fi

PYTHONPATH=bin:../$WEEWX/bin $PYTHON -m unittest discover bin/user/tests