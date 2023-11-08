
#! /bin/bash
#
#    Copyright (c) 2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
source ./devtools/python_versions.sh

if [ -z "$1" ]; then
    WEEWX=weewx4
else
    WEEWX=$1
fi

if [ -z "$2" ]; then
    if [ "$WEEWX" = "weewx3" ]; then
        PY_VERSION=$weewx3_default_python_version
    else
        PY_VERSION=$weewx_default_python_version
    fi    
else
    PY_VERSION=$2
fi

while inotifywait -e modify devtools/watchftests.sh bin/user/MQTTSubscribe.py bin/user/tests/func
do
    ./devtools/runftests.sh $WEEWX $PY_VERSION
done