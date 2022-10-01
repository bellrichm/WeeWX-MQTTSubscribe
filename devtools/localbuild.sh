#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
export BUILDTYPE="LOCAL"

export APPVEYOR_BUILD_VERSION="local"
## $env:APPVEYOR_BUILD_FOLDER =  Split-Path $MyInvocation.MyCommand.Path

# pretend its an appveyor build for coveralls.io/coveralls.net.exe
export APPVEYOR="true"
export APPVEYOR_JOB_ID=get-random

export APPVEYOR_REPO_BRANCH="local"
# $env:APPVEYOR_REPO_COMMIT=
# $env:APPVEYOR_REPO_COMMIT_MESSAGE =
# $env:APPVEYOR_REPO_COMMIT_AUTHOR =
# $env:APPVEYOR_REPO_COMMIT_AUTHOREMAIL =
# $env:APPVEYOR_PULL_REQUEST_NUMBER =

export APPVEYOR_BUILD_WORKER_IMAGE="Ubuntu"

# could not fake out codecov
#export CODECOVIO_UPLOAD="true"
#export CI="true"

# doesn't show source because no commit
#export COVERALLS_UPLOAD="true"

# version of sonar runner installed locally
export SONAR_SCANNER_VERSION="4.2.0.1873"
# Run sonar locally
# this is the most important to run locally, because it does additional analysis
export SONAR_UPLOAD="true"

export ENABLED="true"

# set api keys
# this is separate to help ensure it is not accidentally checked in
source ./localtools/init.sh

source ./appveyor/init.sh
./appveyor/build_script.sh
./appveyor/test_script.sh
./appveyor/after_test.sh

mv -f results* tmp
