 PYTHONPATH=bin nosetests ./bin/user/tests/unit --exe --exclude=setup --cover-package=user.MQTTSubscribe --with-xunit --with-coverage --cover-branches --cover-xml --verbosity=1
 find "$APPVEYOR_BUILD_FOLDER" -type f -name 'nosetests.xml' -print0 | xargs -0 -I '{}' curl -F 'file=@{}' "https://ci.appveyor.com/api/testresults/junit/$APPVEYOR_JOB_ID"

 PYTHONPATH=bin:./weewx/bin nosetests ./bin/user/tests/func --exe --exclude=setup --cover-package=user.MQTTSubscribe --with-xunit --with-coverage --cover-branches --cover-xml --xunit-file=nosetests2.xml --verbosity=1
 find "$APPVEYOR_BUILD_FOLDER" -type f -name 'nosetests2.xml' -print0 | xargs -0 -I '{}' curl -F 'file=@{}' "https://ci.appveyor.com/api/testresults/junit/$APPVEYOR_JOB_ID"

 