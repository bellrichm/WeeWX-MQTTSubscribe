#! /bin/bash
if [ -z "$1" ]
then
    WEEWX=weewx
else
    WEEWX=$1
fi

while inotifywait -e modify bin/user/MQTTSubscribe.py bin/user/tests
do
PYTHONPATH=bin:../weewx/bin python2 -m unittest discover bin/user/tests
PYTHONPATH=bin:../weewx/bin python3 -m unittest discover bin/user/tests
done
