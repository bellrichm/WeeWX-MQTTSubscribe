#! /bin/bash

PYTHONPATH=bin:../weewx3/bin python2 -m unittest discover bin/user/tests
PYTHONPATH=bin:../weewx4/bin python2 -m unittest discover bin/user/tests
PYTHONPATH=bin:../weewx4/bin python3 -m unittest discover bin/user/tests