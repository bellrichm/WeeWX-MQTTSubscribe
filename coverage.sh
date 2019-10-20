WEEWX=weewx_3.9.2
COVERAGE=coverage2
PYTHONPATH=bin:../$WEEWX/bin $COVERAGE run  -m unittest discover bin/user/tests; $COVERAGE html --include bin/user/MQTTSubscribe.py