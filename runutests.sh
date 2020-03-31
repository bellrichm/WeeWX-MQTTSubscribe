#! /bin/bash

echo "Running python 2"
PYTHONPATH=bin python2 -m unittest discover bin/user/tests/unit
echo "Running python 3"
PYTHONPATH=bin python3 -m unittest discover bin/user/tests/unit