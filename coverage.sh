#! /bin/bash
if [ -z "$1" ]
then
    WEEWX=weewx3
else
    WEEWX=$1
fi

if [ -z "$2" ]
then
    COVERAGE=coverage2
else
    COVERAGE=$2
fi

PYTHONPATH=bin:../$WEEWX/bin $COVERAGE run  -m unittest discover bin/user/tests/unit; $COVERAGE html --include bin/user/MQTTSubscribe.py