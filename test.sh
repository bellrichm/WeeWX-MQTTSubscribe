#! /bin/bash
if [ -z "$1" ]
then
    exit 4
else
    TEST=$1
fi

PYTHONPATH=bin python2 bin/user/tests/$TEST
PYTHONPATH=bin python3 bin/user/tests/$TEST