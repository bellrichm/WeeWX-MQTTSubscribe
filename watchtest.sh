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


while inotifywait -e modify bin/user/MQTTSubscribe.py bin/user/tests/$TEST
do
PYTHONPATH=bin:../$WEEWX/bin python2 bin/user/tests/$TEST
PYTHONPATH=bin:../$WEEWX/bin python3 bin/user/tests/$TEST
done