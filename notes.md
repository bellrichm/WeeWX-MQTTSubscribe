Miscellaneous notes:
WeeWX performs quality control on both loop packets and archive records. But, if the archive reocord is created via software generation it is not quality controlled. This is because the data has already been quality contolled as loop packet data. This means that when SubscribeService is bound to new archive records and the controlling service (typically StdArchive) is using software generation, the fields added by SubscribeService are not quality controlled.

When augment_record is true, StdArchive will augment the archive record with fields that are found only in the loop packets. This means that when the Subscribe service is bound to the loop packet it can let StdArchive get the data to the archive record.

StdConvert converts loop packets into the appropriate units. Therefore SubscribeDriver does not have to. Note, SubscribeService still does because it is adding data to a loop packet or archive record and all the data must be in the same units.

SubscribeDriver essentially emits each MQTT payload as a loop packet and lets WeeWX do its "magic" to handle partial packets, units, accumulation, augmentation, etc.

It seems like binding the SubscribeService to loop packets is the more natural fit. This does mean that the MQTT payload has to be accumulated for every loop packet instead of every archive record. This additional processing may put more load on the system, but each cycle of accumulating loop packet will have less data to process. So...


Developer notes:
Assumes that a WeeWX install in weewx directory is a sibling directory to this projects root directory.
I find it useful to symlink the weewx directory to a specific version of weewx.
This allows easily running against different WeeWX versions.

Testing
pip install mock
pip3 install mock

sudo pip install coverage
sudo pip3 install coverage

Debugging specific  MQTT payloads
use pubmqtt.py to publish the payload
- by default it reads from tmp/messages.txt
- each line is an MQTT message
- debug MQTTSubscribe using 'Driver: Loop'
==========================================================================
PYTHONPATH=bin:../weewx/bin coverage2 run  -m unittest discover bin/user/tests; coverage html --include bin/user/MQTTSubscribe.py

coverage3 - for python 3

PYTHONPATH=bin:../weewx/bin python -m unittest discover bin/user/tests

PYTHONPATH=bin:../weewx/bin python bin/user/tests/test_MQTTSubscribe.py

python3 - for python 3

./mqtt_test.py weewx.loop.conf --type=driver --records=1
./mqtt_test.py weewx.loop.conf --type=service --records=1

./mqtt_test.py weewx.archive.conf --type=driver  --records=1
./mqtt_test.py weewx.archive.conf --type=service --records=1