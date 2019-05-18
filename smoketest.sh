PYTHON=python

PYTHONPATH=bin $PYTHON bin/user/MQTTSubscribe.py weewx.conf --type service --binding loop --records 3 --interval 2 --delay 0 --verbose
PYTHONPATH=bin $PYTHON bin/user/MQTTSubscribe.py weewx.conf --type driver --binding loop --records 3 --interval 2 --delay 0 --verbose

PYTHONPATH=bin $PYTHON bin/user/MQTTSubscribe.py weewx.conf --type service --binding archive --records 3 --interval 60 --delay 25 --verbose
PYTHONPATH=bin $PYTHON bin/user/MQTTSubscribe.py weewx.conf --type driver --binding archive --records 3 --interval 60 --delay 25 --verbose
