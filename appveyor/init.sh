#
#    Copyright (c) 2020-2024 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
export SONAR_SCANNER_HOME=$HOME/.sonar/sonar-scanner-$SONAR_SCANNER_VERSION-linux
export PATH=$SONAR_SCANNER_HOME/bin:$PATH

# Add path for things like pytest
export PATH=~/.local/bin:$PATH

if [ "$APPVEYOR_REPO_TAG" = "true" ]; then
  export APPVEYOR_REPO_BRANCH=$APPVEYOR_REPO_TAG_NAME # hack
  export APPVEYOR_BUILD_VERSION=release-$APPVEYOR_REPO_TAG_NAME
  appveyor UpdateBuild -Version "release-$APPVEYOR_REPO_TAG_NAME"
fi
