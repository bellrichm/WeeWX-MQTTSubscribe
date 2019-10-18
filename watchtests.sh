

while inotifywait -e modify bin/user/MQTTSubscribe.py bin/user/tests
do
PYTHONPATH=/home/pi/weewx/bin python2 -m unittest discover bin/user/tests
PYTHONPATH=/home/pi/weewx/bin python3 -m unittest discover bin/user/tests
done
