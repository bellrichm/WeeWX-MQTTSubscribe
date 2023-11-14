#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
# Reminder, tags are uploaded to both coveralls and sonar as a branch with the tag name

if [ "$ENABLED" != "true" ]; then
  exit 0
fi

# do not run on pull requests
if [ "$BUILDTYPE" != "LOCAL" ] && [ "$APPVEYOR_PULL_REQUEST_NUMBER" != "" ]; then
  exit 0
fi

# only upload for one build image
if [ "$APPVEYOR_BUILD_WORKER_IMAGE" != "Ubuntu" ]; then
  exit 0
fi

# only upload once
if [ "$CODECOVIO_UPLOAD" = "true" ]; then
  bash <(curl -s https://codecov.io/bash) -f coverage.xml -F unitests -n unitests-$PYTHON #>/dev/null
  bash <(curl -s https://codecov.io/bash) -f coverage2.xml -F integration -n integration-$PYTHON #/dev/null
fi

# only upload once
if [ "$COVERALLS_UPLOAD" = "true" ]; then
  #COVERALLS_PARALLEL=true coveralls
  # coveralls uses the .coverage file
  # get the one from the unit tests
  cp .coverage1 .coverage
  coveralls
fi

# patch up dirs for sonar
#sed -i 's/classname="/classname="bin\/user\/tests\/unit./g' nosetests.xml
#sed -i 's/classname="/classname="bin\/user\/tests\/integ./g' nosetests2.xml

echo $PATH
echo $JAVA_HOME

# only upload once
if [ "$SONAR_UPLOAD" = "true" ]; then
  sonar-scanner \
    -Dsonar.organization=bellrichm \
    -Dsonar.projectKey=bellrichm_WeeWX-MQTTSubscribe \
    -Dsonar.projectVersion=$APPVEYOR_BUILD_VERSION \
    -Dsonar.branch.name=$APPVEYOR_REPO_BRANCH \
    -Dsonar.sources=./bin/user/MQTTSubscribe.py \
    -Dsonar.tests=./bin/user/tests \
    -Dsonar.language=py \
    -Dsonar.python.xunit.reportPath=results*.xml \
    -Dsonar.python.xunit.skipDetails=false \
    -Dsonar.python.coverage.reportPaths=coverage.xml \
    -Dsonar.python.coveragePlugin=cobertura \
    -Dsonar.python.pylint.reportPath=pylint.txt \
    -Dsonar.host.url=https://sonarcloud.io \
    -Dsonar.login=$SKEY \
    -X
fi
