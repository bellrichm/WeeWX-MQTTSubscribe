

while inotifywait -e modify bin/user/MQTTSubscribe.py bin/user/tests
do
PYTHONPATH=/home/pi/weewx/bin python -m unittest discover bin/user/tests
done
