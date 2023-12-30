#! /bin/bash
#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
source ./devtools/python_versions.sh

export PYENV_VERSION=$weewx_default_python_version
PYTHONPATH=bin coverage run --branch -m pytest bin/user/tests/unit; 

coverage html --include bin/user/MQTTSubscribe.py
