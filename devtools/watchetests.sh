
#! /bin/bash
#
#    Copyright (c) 2025 Rich Bell <bellrichm@gmail.com>
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

./devtools/runftests.sh $WEEWX $PY_VERSION

while inotifywait -e modify devtools/watchetests.sh devtools/runetests.sh bin/user/MQTTSubscribe.py bin/user/tests/e2e
do
    ./devtools/runetests.sh $WEEWX $PY_VERSION
done
