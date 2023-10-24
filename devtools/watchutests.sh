#! /bin/bash
#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
source ./devtools/python_versions.sh

while inotifywait -e modify devtools/watchutests.sh bin/user/MQTTSubscribe.py bin/user/tests/unit
do
    export PYENV_VERSION=$weewx3_default_python_version
    PYTHONPATH=bin python -m unittest discover bin/user/tests/unit

    export PYENV_VERSION=$weewx4_default_python_version
    PYTHONPATH=bin python -m unittest discover bin/user/tests/unit
done
