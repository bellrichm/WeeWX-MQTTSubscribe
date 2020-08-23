export BUILDTYPE="LOCAL"

export APPVEYOR_BUILD_VERSION="local"
## $env:APPVEYOR_BUILD_FOLDER =  Split-Path $MyInvocation.MyCommand.Path

# pretend its an appveyor build for coveralls.io/coveralls.net.exe
export APPVEYOR="true"
export APPVEYOR_JOB_ID=get-random

exportAPPVEYOR_REPO_BRANCH="local"
# $env:APPVEYOR_REPO_COMMIT=
# $env:APPVEYOR_REPO_COMMIT_MESSAGE =
# $env:APPVEYOR_REPO_COMMIT_AUTHOR =
# $env:APPVEYOR_REPO_COMMIT_AUTHOREMAIL =
# $env:APPVEYOR_PULL_REQUEST_NUMBER =

export ENABLED="true"

./appveyor/init.sh
./appveyor/build_script.sh
./appveyor/test_script.sh