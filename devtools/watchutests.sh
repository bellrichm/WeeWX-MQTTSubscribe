#! /bin/bash
#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
while inotifywait -e modify devtools/watchutests.sh bin/user/MQTTSubscribe.py bin/user/tests/unit
do
PYTHONPATH=bin python2 -m unittest discover bin/user/tests/unit
PYTHONPATH=bin python3 -m unittest discover bin/user/tests/unit
done
