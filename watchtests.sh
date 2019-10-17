

while inotifywait -e modify bin/user/MQTTSubscribe.py 
do
PYTHONPATH=/home/pi/weewx/bin python -m unittest discover bin/user/tests
done
