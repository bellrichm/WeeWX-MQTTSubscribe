#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
if [ "$ENABLED" != "true" ]; then
  exit 0
fi

if [ "$BUILDTYPE" = "LOCAL" ]; then
  #HTML_OPTIONS=" --cover-html --with-html "
	HTML_OPTIONS=" --cov-report html:cover "
fi
 #PYTHONPATH=bin nosetests ./bin/user/tests/unit --exe --exclude=setup --cover-package=user.MQTTSubscribe --with-xunit --with-coverage --cover-branches --cover-xml --logging-level=ERROR --verbosity=1 $HTML_OPTIONS
 PYTHONPATH=bin pytest ./bin/user/tests/unit --junitxml=results.xml --cov-report xml:coverage.xml --verbosity=1 --log-level=ERROR --cov=user.MQTTSubscribe --cov-branch $HTML_OPTIONS
 rc=$?
 
# ToDo - option to not exit on error - gor debugging
if [ $rc -ne 0 ]; then
  echo "$rc"
  exit $rc
fi

if [ "$BUILDTYPE" = "LOCAL" ]; then
  #HTML_OPTIONS=" --cover-html --with-html --html-file=nosetests2.html --cover-html-dir=cover2 "
  HTML_OPTIONS=" --cov-report html:cover2 "
  PPATH="../weewx/bin/"
else
  PPATH="./weewx/bin/"  
fi

 #PYTHONPATH=bin:$PPATH nosetests ./bin/user/tests/integ --exe --exclude=setup --cover-package=user.MQTTSubscribe --with-xunit --with-coverage --cover-branches --cover-xml  --cover-xml-file=coverage2.xml --xunit-file=nosetests2.xml --logging-level=ERROR --verbosity=1 $HTML_OPTIONS
 PYTHONPATH=bin:$PPATH pytest ./bin/user/tests/integ --junitxml=results2.xml --cov-report xml:coverage2.xml --verbosity=1 --log-level=ERROR --cov=user.MQTTSubscribe --cov-branch $HTML_OPTIONS
 rc=$?

if [ "$BUILDTYPE" != "LOCAL" ]; then
  find "$APPVEYOR_BUILD_FOLDER" -type f -name 'results.xml' -print0 | xargs -0 -I '{}' curl -F 'file=@{}' "https://ci.appveyor.com/api/testresults/junit/$APPVEYOR_JOB_ID"
  find "$APPVEYOR_BUILD_FOLDER" -type f -name 'results2.xml' -print0 | xargs -0 -I '{}' curl -F 'file=@{}' "https://ci.appveyor.com/api/testresults/junit/$APPVEYOR_JOB_ID"
fi
exit $rc
