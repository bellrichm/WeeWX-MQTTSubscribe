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
    export PYENV_VERSION=$weewx_default_python_version    
else
    export PYENV_VERSION=$2
fi

# Note, the value for $WEEWX can be relative. For example ../weewx-source/weewx-3.7.1

./devtools/runutests.sh $WEEWX $PYENV_VERSION

./devtools/runitests.sh $WEEWX $PYENV_VERSION

echo "Completed $python_version $WEEWX"
