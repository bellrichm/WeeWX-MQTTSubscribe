#! /bin/bash
PYTHONPATH=bin coverage3 run -p --branch -m unittest discover bin/user/tests/unit; 
PYTHONPATH=bin coverage2 run -p --branch -m unittest discover bin/user/tests/unit; 
coverage combine
coverage html --include bin/user/MQTTSubscribe.py