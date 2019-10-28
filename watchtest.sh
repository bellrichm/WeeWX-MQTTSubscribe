#! /bin/bash
if [ -z "$1" ]
then
    exit 4
else
    TEST=$1
fi

while inotifywait -e modify bin/user/MQTTSubscribe.py bin/user/tests/$TEST
do
PYTHONPATH=bin:../weewx3/bin python2 bin/user/tests/$TEST
PYTHONPATH=bin:../weewx4/bin python2 bin/user/tests/$TEST
PYTHONPATH=bin:../weewx4/bin python3 bin/user/tests/$TEST
done