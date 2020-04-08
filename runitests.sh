#! /bin/bash

echo "Running python 2 weewx 4"
PYTHONPATH=bin:../weewx4/bin python2 -m unittest discover bin/user/tests/func
echo "Running python 3 weewx 4"
PYTHONPATH=bin:../weewx4/bin python3 -m unittest discover bin/user/tests/func
echo "Running python 2 weewx 3"
PYTHONPATH=bin:../weewx3/bin python2 -m unittest discover bin/user/tests/func


