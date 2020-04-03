coveralls

sed -i 's/classname="/classname="bin\/user\/tests\/unit./g' nosetests.xml
sed -i 's/classname="/classname="bin\/user\/tests\/func./g' nosetests2.xml

sonar-scanner \
  -Dsonar.organization=bellrichm \
  -Dsonar.projectKey=bellrichm_WeeWX-MQTTSubscribe \
  -Dsonar.sources=./bin/user/MQTTSubscribe.py \
  -Dsonar.tests=./bin/user/tests \
  -Dsonar.language=py \
  -Dsonar.python.xunit.reportPath=nosetests*.xml \
  -Dsonar.python.xunit.skipDetails=false \
  -Dsonar.python.coverage.reportPaths=coverage.xml \
  -Dsonar.python.coveragePlugin=cobertura \
  -Dsonar.python.pylint.reportPath=pylint.txt \
  -Dsonar.host.url=https://sonarcloud.io \
  -Dsonar.login=$SKEY \
  #-X

