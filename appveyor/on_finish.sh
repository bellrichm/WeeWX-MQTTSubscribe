#
#    Copyright (c) 2020-2024 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
 if [ "$ENABLE_SSH_AT_END" = "true" ]; then
    export APPVEYOR_SSH_BLOCK=true
    curl -sflL 'https://raw.githubusercontent.com/appveyor/ci/master/scripts/enable-ssh.sh' | bash -e -
fi
