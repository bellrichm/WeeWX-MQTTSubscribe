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
elif [ -z "$2" ]; then
    WEEWX_VERSION=$weewx_default_version
    PY_VERSION=$1
else
    WEEWX_VERSION=$1
    PY_VERSION=$2
fi

while inotifywait -e modify devtools/watchlints.sh devtools/runlints.sh .pylintrc ./*.py ./bin/user ./bin/user/tests/unit/*.py ./bin/user/tests/func/*.py ./bin/user/tests/integ/*.py
do
    ./devtools/runlints.sh $WEEWX_VERSION $PY_VERSION
done
