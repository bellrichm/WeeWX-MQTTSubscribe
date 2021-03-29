#! /bin/bash
#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
PYTHONPATH=bin coverage3 run -p --branch -m unittest discover bin/user/tests/unit; 
PYTHONPATH=bin coverage2 run -p --branch -m unittest discover bin/user/tests/unit; 
coverage combine
coverage html --include bin/user/MQTTSubscribe.py
