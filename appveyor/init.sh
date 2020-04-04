export SONAR_SCANNER_HOME=$HOME/.sonar/sonar-scanner-$SONAR_SCANNER_VERSION-linux
export PATH=$SONAR_SCANNER_HOME/bin:$PATH

if [ "$APPVEYOR_REPO_TAG" = "true" ]; then
  export APPVEYOR_BUILD_VERSION=$APPVEYOR_REPO_TAG
  appveyor UpdateBuild -Version "$APPVEYOR_REPO_TAG_NAME"
fi