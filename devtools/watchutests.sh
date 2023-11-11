#! /bin/bash
#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
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
    $PY_VERSION=$weewx_default_python_version    
else
    $PY_VERSIONION=$2
fi

while inotifywait -e modify devtools/watchutests.sh devtools/runutests.sh bin/user/MQTTSubscribe.py bin/user/tests/unit
do
    ./devtools/runutests.sh $WEEWX $PY_VERSION
done
