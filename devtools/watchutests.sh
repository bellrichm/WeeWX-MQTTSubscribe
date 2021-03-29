#! /bin/bash

while inotifywait -e modify devtools/watchutests.sh bin/user/MQTTSubscribe.py bin/user/tests/unit
do
PYTHONPATH=bin python2 -m unittest discover bin/user/tests/unit
PYTHONPATH=bin python3 -m unittest discover bin/user/tests/unit
done
