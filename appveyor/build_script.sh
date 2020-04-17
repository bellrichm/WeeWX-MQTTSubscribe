if [ "$ENABLED" != "true" ]; then
  exit 0
fi

PYTHONPATH=./weewx/bin pylint ./bin/user/MQTTSubscribe.py -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" | tee pylint.txt
rc=${PIPESTATUS[0]}
detail=`cat pylint.txt`

if [ $rc -eq 0 ]; then
  category="Information"
  build_rc=0
elif [ $rc -gt 2 ]; then
  category="Warning"
  build_rc=0
else
  category="Error"
  build_rc=1
fi

appveyor AddMessage "pylint weewx=$WEEWX python=$PYTHON rc=$rc " -Category $category -Details "$detail"

exit $build_rc