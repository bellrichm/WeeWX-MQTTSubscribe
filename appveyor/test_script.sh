if [ "$ENABLED" != "true" ]; then
  exit 0
fi

 PYTHONPATH=bin nosetests ./bin/user/tests/unit --exe --exclude=setup --cover-package=user.MQTTSubscribe --with-xunit --with-coverage --cover-branches --cover-xml --logging-level=ERROR --verbosity=1
 rc=$?
 find "$APPVEYOR_BUILD_FOLDER" -type f -name 'nosetests.xml' -print0 | xargs -0 -I '{}' curl -F 'file=@{}' "https://ci.appveyor.com/api/testresults/junit/$APPVEYOR_JOB_ID"
# ToDo - option to not exit on error - gor debugging
if [ $rc -ne 0 ]; then
  echo "$rc"
  exit $rc
fi

 PYTHONPATH=bin:./weewx/bin nosetests ./bin/user/tests/integ --exe --exclude=setup --cover-package=user.MQTTSubscribe --with-xunit --with-coverage --cover-branches --cover-xml --cover-xml-file=coverage2.xml --xunit-file=nosetests2.xml --logging-level=ERROR --verbosity=1
 rc=$?
 find "$APPVEYOR_BUILD_FOLDER" -type f -name 'nosetests2.xml' -print0 | xargs -0 -I '{}' curl -F 'file=@{}' "https://ci.appveyor.com/api/testresults/junit/$APPVEYOR_JOB_ID"

exit $rc
