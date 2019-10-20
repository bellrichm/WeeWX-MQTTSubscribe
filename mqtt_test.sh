#! /bin/bash
if [ -z "$1" ]
then
    PYTHON=python2
else
    PYTHON=$1
fi

$PYTHON mqtt_test.py weewx.loop.conf --type=driver --records=1
$PYTHON mqtt_test.py weewx.loop.conf --type=service --records=1

$PYTHON mqtt_test.py weewx.archive.conf --type=driver  --records=1
$PYTHON mqtt_test.py weewx.archive.conf --type=service --records=1