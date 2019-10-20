PYTHON=python2
WEEWX=weewx_3.9.2
TEST=test_MQTTSubscribe.py

PYTHONPATH=bin:../$WEEWX/bin $PYTHON bin/user/tests/$TEST