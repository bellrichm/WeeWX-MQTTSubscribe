#! /bin/bash
#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
if [ -z "$1" ]
then
    WEEWX=weewx
else
    WEEWX=$1
fi

if [ -z "$2" ]
then
    PYTHON=python2
else
    PYTHON=$2
fi

PYTHONPATH=bin:../$WEEWX/bin $PYTHON bin/user/MQTTSubscribe.py devtools/weewx.loop.conf --type service --binding loop --records 3 --interval 2 --delay 0 --verbose
PYTHONPATH=bin:../$WEEWX/bin $PYTHON bin/user/MQTTSubscribe.py devtools/weewx.loop.conf --type driver --binding loop --records 3 --interval 2 --delay 0 --verbose

PYTHONPATH=bin:../$WEEWX/bin $PYTHON bin/user/MQTTSubscribe.py devtools/weewx.archive.conf --type service --binding archive --records 3 --interval 60 --delay 5 --verbose
PYTHONPATH=bin:../$WEEWX/bin $PYTHON bin/user/MQTTSubscribe.py devtools/weewx.archive.conf --type driver --binding archive --records 3 --interval 2 --delay 0 --verbose
