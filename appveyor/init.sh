#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
export SONAR_SCANNER_HOME=$HOME/.sonar/sonar-scanner-$SONAR_SCANNER_VERSION-linux
export PATH=$SONAR_SCANNER_HOME/bin:$PATH

if [ "$APPVEYOR_REPO_TAG" = "true" ]; then
  export APPVEYOR_REPO_BRANCH=$APPVEYOR_REPO_TAG_NAME # hack
  export APPVEYOR_BUILD_VERSION=release-$APPVEYOR_REPO_TAG_NAME
  appveyor UpdateBuild -Version "release-$APPVEYOR_REPO_TAG_NAME"
fi

if [ "$APPVEYOR_BUILD_WORKER_IMAGE" = "Previous Ubuntu1604" ] && [ "$PYTHON" = "3.6.15" ]; then
  echo "$APPVEYOR_BUILD_WORKER_IMAGE with $PYTHON is broken on Appveyor."
  export ENABLED="false"
fi

if [ "$APPVEYOR_BUILD_WORKER_IMAGE" = "Previous Ubuntu1604" ] && [ "$PYTHON" = "3.10" ]; then
  echo "$APPVEYOR_BUILD_WORKER_IMAGE with $PYTHON is broken on Appveyor."
  export ENABLED="false"
fi