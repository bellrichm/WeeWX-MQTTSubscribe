#! /bin/bash
#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
source ./devtools/python_versions.sh

if [ -z "$1" ]; then
    WEEWX=weewx5
else
    WEEWX=$1
fi

if [ -z "$2" ]; then
    export PYENV_VERSION=$weewx_default_python_version    
else
    export PYENV_VERSION=$2
fi

python_command='python'$PYENV_VERSION
python_version=$(pyenv which $python_command)
echo "Running $python_version $WEEWX"

# todo - get running as a driver to work 

echo "Running as service bound to loop"
PYTHONPATH=bin:../$WEEWX/src:../$WEEWX/bin python bin/user/MQTTSubscribe.py simulate service --conf devtools/smoketest.loop.conf --binding loop --records 3 --logging-level DEBUG
echo "Running as driver bound to loop"
PYTHONPATH=bin:../$WEEWX/src:../$WEEWX/bin python bin/user/MQTTSubscribe.py simulate driver --conf devtools/smoketest.loop.conf --binding loop --records 3 --archive-delay 0 --logging-level DEBUG

echo "Running as service bound to archive"
PYTHONPATH=bin:../$WEEWX/src:../$WEEWX/bin python bin/user/MQTTSubscribe.py simulate service --conf devtools/smoketest.archive.conf --binding archive --records 3 --logging-level DEBUG
echo "Running as driver bound to archive"
PYTHONPATH=bin:../$WEEWX/src:../$WEEWX/bin python bin/user/MQTTSubscribe.py simulate driver --conf devtools/smoketest.archive.conf --binding archive --records 3 --archive-interval 60 --archive-delay 5 --logging-level DEBUG
