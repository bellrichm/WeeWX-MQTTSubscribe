 if [ "$ENABLE_SSH" = "true" ]; then
    export APPVEYOR_SSH_BLOCK=true
    curl -sflL 'https://raw.githubusercontent.com/appveyor/ci/master/scripts/enable-ssh.sh' | bash -e -
fi