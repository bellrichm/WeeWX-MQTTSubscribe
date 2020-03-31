#! /bin/bash

if [ -z "$1" ]
then
    COVERAGE=coverage2
else
    COVERAGE=$1
fi

PYTHONPATH=bin $COVERAGE run  -m unittest discover bin/user/tests/unit; $COVERAGE html --include bin/user/MQTTSubscribe.py