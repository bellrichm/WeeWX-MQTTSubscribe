if [ "$ENABLED" != "true" ]; then
  exit 0
fi

PYTHONPATH=./weewx/bin pylint ./bin/user/MQTTSubscribe.py -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" | tee pylint.txt
rc = $?

appveyor AddMessage "test $rc" -Details `cat pylint.txt`