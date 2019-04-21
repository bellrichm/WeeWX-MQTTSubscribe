# WeeWX-MQTTSubscribe
A Weewx service and driver that receives data from MQTT

## Description

### Service
The service can bind to either new loop packets or new archive records. In both cases a separate thread captures the MQTT payload and puts it on a queue. On new packets/records events, the main thread takes all the elements from the queue with a dateTime that is less than the packet's/record's dateTime. These elements are accumulated to a single set of data fields. if necessary, the data is converted to the units of the packet/record. The packet/record is then updated with the data.

In development, it was noticed that due to the shorter interval, sometimes the MQTT payload was "dropped" because it dateTime was smaller than the expected start (the previous packet's dateTime). The option, overlap, can be set to decrement the start time and capture the payload. This value should be as small as possible.

### Driver
The driver also captures the MQTT payload in a separate thread. Then in genLoopPackets, every element is in the queue is turned into a packet. 
It is also possible to subscribe to a second topic. The MQTT payload from this topic is put into a separate queue. This queue is processed by the genArchiveRecords to create archive records. With the combination of the two topics/queues, one can have a WeeWX instance gather the data and publish loop and archive data for other instances to receive.

When generating loop packets and the queue becomes empty, the option, wait_before_retry, controls how long before an attempt is made to get data from the queue.

## Running stand-alone 
To aid in development and debugging, both the service and driver can be run "stand-alone" via

```
PYTHONPATH=bin python bin/user/MQTTSubscribe.py <options> weewx.conf
```

Where the options are:

```
--verbose 
    Verbose logging
--type [driver|service] 
    Run  as driver or service
--records N
    Create N records or packets
--interval N
    Number of seconds between packet or record generation.
--delay N
    Number of seconds delay to wait after the archive period is over
--binding [archive|loop]
    Bind to either new packets or records when running the service.
    Process loop/packet or archive.record when running the driver.
--units [US|METRIC|METRICWX]
    The units of the packet/record passed to the service. Only used when running the service.
```

Examples:
Bind the service to new archive records and update two records.

```
PYTHONPATH=bin python bin/user/MQTTSubscribe.py --type service --binding archive --interval 300 --delay 15 --records 2 weewx.conf
```

Run as a driver every 2 seconds generate a loop packet for a total of 30.

```
PYTHONPATH=bin python bin/user/MQTTSubscribe.py --type driver --binding loop --interval 2 --records 30 weewx.conf
```

## Manual installation Instructions

1. Install the paho MQTT client.

    ```
    sudo pip install paho-mqtt
    ```

2. For the driver, update the station type and configure the driver as required. See comments in MQTTSubscribe for configuration information.

    ```
    [Station]
        station_type = MQTTSubscribeDriver
    
    [MQTTSubscribeDriver]
        driver = user.MQTTSubscribe
        host = localhost
        payload_type = json
    ```
    
3. For the service, configure as required and add the service to WeeWX. See comments in MQTTSubscribe for configuration information.

    ```
    [MQTTSubscribeService]
        host = localhost
        payload_type = json

    [Engine]
        [[Services]]
            data_services = user.MQTTSubscribe.MQTTSubscribeService
     ```
     