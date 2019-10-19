PYTHON=python

PYTHONPATH=bin:../weewx/bin $PYTHON bin/user/MQTTSubscribe.py weewx.loop.conf --type service --binding loop --records 3 --interval 2 --delay 0 --verbose
PYTHONPATH=bin:../weewx/bin $PYTHON bin/user/MQTTSubscribe.py weewx.loop.conf --type driver --binding loop --records 3 --interval 2 --delay 0 --verbose

PYTHONPATH=bin:../weewx/bin $PYTHON bin/user/MQTTSubscribe.py weewx.archive.conf --type service --binding archive --records 3 --interval 60 --delay 5 --verbose
PYTHONPATH=bin:../weewx/bin $PYTHON bin/user/MQTTSubscribe.py weewx.archive.conf --type driver --binding archive --records 3 --interval 2 --delay 0 --verbose
