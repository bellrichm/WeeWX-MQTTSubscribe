#! /bin/bash

echo "Running WeeWX 3 with python 2"
PYTHONPATH=bin:../weewx3/bin python2 -m unittest discover bin/user/tests/unit
echo "Running WeeWX 4 with python 2"
PYTHONPATH=bin:../weewx4/bin python2 -m unittest discover bin/user/tests/unit
echo "Running WeeWX 4 with python 3"
PYTHONPATH=bin:../weewx4/bin python3 -m unittest discover bin/user/tests/unit