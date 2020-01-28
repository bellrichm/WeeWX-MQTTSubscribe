#! /bin/bash

while inotifywait -e modify watchtests.sh bin/user/MQTTSubscribe.py bin/user/tests
do
PYTHONPATH=bin:../weewx3/bin python2 -m unittest discover bin/user/tests
PYTHONPATH=bin:../weewx4/bin python2 -m unittest discover bin/user/tests
PYTHONPATH=bin:../weewx4/bin python3 -m unittest discover bin/user/tests
done
