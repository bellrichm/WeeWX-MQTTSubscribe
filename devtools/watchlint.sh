#! /bin/bash
#
#    Copyright (c) 2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
source ./devtools/python_versions.sh

if [ -z "$1" ]; then
    WEEWX_VERSION=$weewx_default_version
    PY_VERSION=$weewx_default_python_version
    CODE="bin/user/MQTTSubscribe.py"
elif [ -z "$2" ]; then
    WEEWX_VERSION=$weewx_default_version
    PY_VERSION=$weewx_default_python_version
    CODE=$1
elif [ -z "$3" ]; then
    WEEWX_VERSION=$weewx_default_version
    PY_VERSION=$1
    CODE=$2
else
    WEEWX_VERSION=$1
    PY_VERSION=$2
    CODE=$3
fi

while inotifywait -e modify devtools/watchlint.sh devtools/lint.sh $CODE

do
    ./devtools/lint.sh $WEEWX_VERSION $PY_VERSION $CODE
done
