#! /bin/bash
#
#    Copyright (c) 2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
source ./devtools/python_versions.sh

if [ -z "$1" ]; then
    exit 4
elif [ -z "$2" ]; then
    WEEWX_VERSION=$weewx_default_version
    PY_VERSION=$weewx_default_python_version
    TEST=$1
elif [ -z "$3" ]; then
    WEEWX_VERSION=$weewx_default_version
    PY_VERSION=$1
    TEST=$2
else
    WEEWX_VERSION=$1
    PY_VERSION=$2
    TEST=$3
fi

while inotifywait -e modify devtools/watchitest.sh devtools/itest.sh bin/user/MQTTSubscribe.py bin/user/tests/integ/utils.py bin/user/tests/integ/data bin/user/tests/integ/$TEST
do
    ./devtools/itest.sh $WEEWX_VERSION $PY_VERSION $TEST
done
