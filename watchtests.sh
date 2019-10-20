WEEWX=weewx_3.9.2

while inotifywait -e modify bin/user/MQTTSubscribe.py bin/user/tests
do
PYTHONPATH=bin:../weewx/bin python2 -m unittest discover bin/user/tests
PYTHONPATH=bin:../weewx/bin python3 -m unittest discover bin/user/tests
done
