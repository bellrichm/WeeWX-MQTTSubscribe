#! /bin/bash
#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
source ./devtools/python_versions.sh

if [ -z "$1" ]
then
    exit 4
else
    TEST=$1
fi

while inotifywait -e modify devtools/watchutest.sh bin/user/MQTTSubscribe.py bin/user/tests/integ/utils.py bin/user/tests/integ/data bin/user/tests/unit/$TEST
do
    export PYENV_VERSION=$weewx3_default_python_version
    PYTHONPATH=bin:../weewx3/bin python bin/user/tests/unit/$TEST

    export PYENV_VERSION=$weewx4_default_python_version
    PYTHONPATH=bin:../weewx4/bin python bin/user/tests/unit/$TEST
done
