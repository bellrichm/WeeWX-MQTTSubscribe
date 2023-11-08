#
#    Copyright (c) 2020-2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
if [ "$ENABLED" != "true" ]; then
  exit 0
fi

if [ "$BUILDTYPE" = "LOCAL" ]; then
  PPATH="../weewx/"
else
  PPATH="./weewx/"
fi

WEEWXBIN="src"
if [ -d "$PPATH""$WEEWXBIN" ]; then
  PPATH="$PPATH""$WEEWXBIN/"
else
  PPATH="$PPATH"bin/
fi

if [ "$BUILDTYPE" = "LOCAL" ]; then
	HTML_OPTIONS=" --cov-report html:cover "
fi
 PYTHONPATH=bin pytest ./bin/user/tests/unit --junitxml=results.xml --cov-report xml:coverage.xml --verbosity=1 --log-level=ERROR --cov=user.MQTTSubscribe --cov-branch $HTML_OPTIONS
 rc=$?

PYTHONPATH=bin:$PPATH pytest ./bin/user/tests/func --junitxml=results3.xml --verbosity=1 --log-level=ERROR 

# coveralls uses this file, so stash a copy
mv .coverage .coverage1

# ToDo - option to not exit on error - gor debugging
if [ $rc -ne 0 ]; then
  echo "$rc"
  exit $rc
fi

if [ "$BUILDTYPE" = "LOCAL" ]; then
  HTML_OPTIONS=" --cov-report html:cover2 "
fi

 PYTHONPATH=bin:$PPATH pytest ./bin/user/tests/integ --junitxml=results2.xml --cov-report xml:coverage2.xml --verbosity=1 --log-level=ERROR --cov=user.MQTTSubscribe --cov-branch $HTML_OPTIONS
 rc=$?

 # coveralls uses this file, so stash a copy
cp .coverage .coverage2

if [ "$BUILDTYPE" != "LOCAL" ]; then
  find "$APPVEYOR_BUILD_FOLDER" -type f -name 'results.xml' -print0 | xargs -0 -I '{}' curl -F 'file=@{}' "https://ci.appveyor.com/api/testresults/junit/$APPVEYOR_JOB_ID"
  find "$APPVEYOR_BUILD_FOLDER" -type f -name 'results3.xml' -print0 | xargs -0 -I '{}' curl -F 'file=@{}' "https://ci.appveyor.com/api/testresults/xunit/$APPVEYOR_JOB_ID"
  find "$APPVEYOR_BUILD_FOLDER" -type f -name 'results2.xml' -print0 | xargs -0 -I '{}' curl -F 'file=@{}' "https://ci.appveyor.com/api/testresults/junit/$APPVEYOR_JOB_ID"
fi
exit $rc
