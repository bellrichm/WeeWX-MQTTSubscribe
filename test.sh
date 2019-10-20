#! /bin/bash
if [ -z "$1" ]
then
    exit 4
else
    TEST=$1
fi

if [ -z "$2" ]
then
    WEEWX=weewx
else
    WEEWX=$2
fi

if [ -z "$3" ]
then
    PYTHON=python2
else
    PYTHON=$3
fi

PYTHONPATH=bin:../$WEEWX/bin $PYTHON bin/user/tests/$TEST