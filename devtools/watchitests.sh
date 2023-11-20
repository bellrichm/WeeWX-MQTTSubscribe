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
    PY_VERSION=$weewx_default_python_version    
else
    PY_VERSION=$2
fi

./devtools/runitests.sh $WEEWX $PY_VERSION

while inotifywait -e modify devtools/watchitests.sh devtools/runitests.sh bin/user/MQTTSubscribe.py bin/user/tests/integ
do
    ./devtools/runitests.sh $WEEWX $PY_VERSION
done
