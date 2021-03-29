#! /bin/bash
#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
if [ -z "$1" ]
then
    WEEWX=weewx4
else
    WEEWX=$1
fi

# Note, the value for $WEEWX can be relative. For example ../weewx-source/weewx-3.7.1

echo "Running python $PYENV_VERSION weewx $WEEWX"

PYTHONPATH=bin:../$WEEWX/bin python -m pylint ./*.py
PYTHONPATH=bin:../$WEEWX/bin python -m pylint ./bin/user
PYTHONPATH=bin:../$WEEWX/bin python -m pylint ./bin/user/tests/unit/*.py -d duplicate-code
PYTHONPATH=bin:../$WEEWX/bin python -m pylint ./bin/user/tests/integ/*.py -d duplicate-code
