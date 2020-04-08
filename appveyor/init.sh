export SONAR_SCANNER_HOME=$HOME/.sonar/sonar-scanner-$SONAR_SCANNER_VERSION-linux
export PATH=$SONAR_SCANNER_HOME/bin:$PATH

if [ "$APPVEYOR_REPO_TAG" = "true" ]; then
  export APPVEYOR_REPO_BRANCH=$APPVEYOR_REPO_TAG_NAME # hack
  export APPVEYOR_BUILD_VERSION=release-$APPVEYOR_REPO_TAG_NAME
  appveyor UpdateBuild -Version "release-$APPVEYOR_REPO_TAG_NAME"
fi