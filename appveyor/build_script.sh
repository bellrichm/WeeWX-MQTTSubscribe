if [ "$ENABLED" != "true" ]; then
  exit 0
fi

PYTHONPATH=./weewx/bin pylint ./bin/user/MQTTSubscribe.py -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" | tee pylint.txt
rc=${PIPESTATUS[0]}
detail=`cat pylint.txt`

appveyor AddMessage "pylint $WEEWX $PYTHON: $rc" -Details "$detail"