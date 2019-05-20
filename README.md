# WeeWX-MQTTSubscribe
A Weewx service and driver that receives data from multiple MQTT topics.

Currently MQTT payloads of json, keyword (field1=value, field2=value..), and individual (each topic contains a single observation) are supported. 

## Description
### **Driver** ### 
The driver captures the MQTT payload in a separate thread. Then in *genLoopPackets*, every element in the queue is turned into its own packet. 

It is also possible to subscribe to a second topic. The MQTT payload from this topic is put into a separate queue. This queue is processed by the *genArchiveRecords* to create archive records (simulating hardware generation). With the combination of the two topics/queues, one can have a WeeWX instance gather the data and publish loop and archive data for other instances to receive.

When generating loop packets and the queue becomes empty, the option, wait_before_retry, controls how long before an attempt is made to get data from the queue.
### **Service**
The service can bind to either new loop packets or new archive records. In both cases a separate thread captures the MQTT payload and puts it on a queue. On new packets/records events, the main thread takes all the elements from the queue with a dateTime that is less than the packet's/record's dateTime. These elements are accumulated to a single set of data fields. If necessary, the data is converted to the units of the packet/record. The packet/record is then updated with the data.

In development, it was noticed that due to the shorter interval, sometimes the MQTT payload was "dropped" because it dateTime was smaller than the expected start (the previous packet's dateTime). The option, overlap, can be set to decrement the start time and capture the payload. This value should be as small as possible.

## Installation and running stand-alone notes
Because there are [multiple methods to install WeeWX](http://weewx.com/docs/usersguide.htm#installation_methods), location of files can vary. See [where to find things](http://weewx.com/docs/usersguide.htm#Where_to_find_things) in the WeeWX [User's Guide](http://weewx.com/docs/usersguide.htm") for the definitive information. The following symbolic names are used to define the various locations:
-   *$DOWNLOAD_ROOT* - The directory containing the downloaded *MQTTSubscribe* extension.
-   *$BIN_ROOT* - The directory where WeeWX executables are located. 
-   *$CONFIG_ROOT* - The directory where the configuration (typicall, weewx.conf) is located.

## Preqrequisites
1. Install the paho MQTT client.

    ```
    pip install paho-mqtt
    ```

## Installation
1. Download MQTTSubscribe

    ```
    wget -P $DOWNLOAD_ROOT https://github.com/bellrichm/WeeWX-MQTTSubscribe/archive/v.X.Y.Z.tar.gz
    ```
2. Install MQTTSubscribe
    * As a driver
    
        ```
        $BIN_ROOT/wee_extension --install=$DOWNLOAD_ROOT/v.X.Y.Z.tar.gz
        $BIN_ROOT/wee_config --reconfig
        ```
        
        **Note:** By default when installing, the service is configured but not enabled. 
        To not install and configure the service (only install the file(s)), 
        set the environment variable MQTTSubscribe_install_type to DRIVER. For example,
        
        ```
        MQTTSubscribe_install_type=DRIVER --install=$DOWNLOAD_ROOT/v.X.Y.Z.tar.gz
        ```
        
        And then configure the driver
        
        ```
        $BIN_ROOT/wee_config --reconfig
        ```
        Edit the [MQTTSubscribeDriver] stanza to configure the topics to subscribe to.
    
    * As a service
    
        ```
        $BIN_ROOT/wee_extension --install=$DOWNLOAD_DIR/v.X.Y.Z.tar.gz
        ```
        
        Edit the [MQTTSubscribeService] stanza as required.
        At the very least the topics to subscribe to must be configured. Other settings such
        as host and port may need to be changed.
            
        **Note:** By default when installing, the service is installed configured but not enabled. 
        To enable, set the environment variable MQTTSubscribe_install_type to SERVICE. For example,
        
        ```
        MQTTSubscribe_install_type=SERVICE --install=$DOWNLOAD_DIR/v.X.Y.Z.tar.gz
        ```
3. Optionally run in standalone mode

    ```
    PYTHONPATH=$BIN_ROOT python $BIN_ROOT/user/MQTTSubscribe.py <options> $CONFIG_ROOT/weewx.conf
    ```
4. Restart WeeWX 

    ```
    sudo /etc/init.d/weewx restart
    ```
    
    or
    
    ```
    sudo sudo service restart weewx
    ```
    
    or 
    
    ``` 
    sudo systemctl restart weewx
    ```

## Manual installation instructions
1. Download MQTTSubscribe

    ```
    wget -P $DOWNLOAD_ROOT https://github.com/bellrichm/WeeWX-MQTTSubscribe/archive/v.X.Y.Z.tar.gz
    ```
2. Unpack MQTTSubscribe

    ```
    tar xvfz v.X.Y.Z.tar.gz
    ```
3. Copy the file

    ```
    cp $DOWNLOAD_ROOT/v.X.Y.X/bin/user/MQTTSubscribe.py $BIN_ROOT/user
    ```
4. Configure
    * As a driver
    
        ```
        $BIN_ROOT/wee_config --reconfig
        ```
        Edit the [MQTTSubscribeDriver] stanza to configure the topics to subscribe to.
        
        ```
        [MQTTSubscribeDriver]
            [[topics]]
                [[[topic1]]]
                [[[topic2]]]
         ```

    * As a service    
        Configure as required and add the service to WeeWX. 
        
        ```
        [MQTTSubscribeService]
            host = localhost
            payload_type = json
            [[topics]]
                [[[topic1]]]
                [[[topic2]]]
        [Engine]
            [[Services]]
                data_services = user.MQTTSubscribe.MQTTSubscribeService
         ```
## Running stand-alone 
To aid in development and debugging, both the service and driver can be run "stand-alone" via:

```
PYTHONPATH=$BIN_ROOT python $BIN_ROOT/user/MQTTSubscribe.py <options> $CONFIG_ROOT/weewx.conf
```

Where the options are:

```
--verbose 
    Verbose logging.
--console
    Write all logging to the console/terminal.
    This will override the setting in weewx.conf.
--type [driver|service] 
    Run  as driver or service
--records N
    Create N records or packets
--interval N
    Number of seconds between packet or record generation.
-- delay N
    The archive delay in seconds.
--delay N
    Number of seconds delay to wait after the archive period is over
--binding [archive|loop]
    Bind to either new packets or records when running the service. 
    This will override the setting in weewx.conf.
    Process loop/packet or archive.record when running the driver.
--units [US|METRIC|METRICWX]
    The units of the packet/record passed to the service. Only used when running the service.
```

Examples:

* Bind the service to new archive records and update two records.

    ```
    PYTHONPATH=$BIN_ROOT python $BIN_ROOT/user/MQTTSubscribe.py $CONFIG_ROOT/weewx.conf --type service --binding archive --interval 300 --delay 15 --records 2 weewx.conf
    ```

* Run as a driver every 2 seconds generate a loop packet for a total of 30.


    ```
    PYTHONPATH=$BIN_ROOT python $BIN_ROOT/user/MQTTSubscribe.py $CONFIG_ROOT/weewx.conf --type driver --binding loop --interval 2 --records 30 weewx.conf
    ```
     