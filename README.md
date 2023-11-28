# WeeWX-MQTTSubscribe

A Weewx service and driver that receives data from multiple MQTT topics.

Currently MQTT payloads of json, keyword (field1=value, field2=value..),
and individual (each topic contains a single observation) are supported.

## Description

### **Driver**

The driver captures the MQTT payload in a separate thread.
Then in *genLoopPackets*, every element in the queue is turned into its own packet.

It is also possible to subscribe to a second topic. The MQTT payload from this topic is put into a separate queue.
This queue is processed by the *genArchiveRecords* to create archive records (simulating hardware generation).
With the combination of the two topics/queues,
one can have a WeeWX instance gather the data and publish loop and archive data for other instances to receive.

When generating loop packets and the queue becomes empty, the option, wait_before_retry,
controls how long before an attempt is made to get data from the queue.

### **Service**

The service can bind to either new loop packets or new archive records.
In both cases a separate thread captures the MQTT payload and puts it on a queue.
On new packets/records events, the main thread takes the elements from the queue and accumulates them into a single dictionary of data fields.
If necessary, the data is converted to the units of the packet/record. The packet/record is then updated with the data.

The elements that are processed from the queue can be controlled by various configuration options.
By default, if the MQTT datetime is less than the previous packet's datetime it is ignored.
This check can be ignored by setting ignore_start_time to True.
It can be controlled more granularly by setting adjust_start_time to the number of seconds prior to the previous packet's datetime is allowed.
Also by default, when the MQTT datetime is greater than the packet's datetime, the pocessing of the queue for this packet stops.
This check can be ignored by setting ignore_end_time to True.
It can be controlled more granularly by setting adjust_end_time to the number of seconds after the packet's datetime is allowed to be processed.

## Installation notes

**To install version 2.x and prior see,
[Installing and Updating Version 2.X and Earlier](https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/Installing-and-updating-version-2.x-and-earlier).**

**Note:** It is rare that MQTTSubscribe should be configured to run as both a `service` and `driver`.
If you are augmenting an existing driver's data, run MQTTSubscribe as a `service`. Otherwise, run it as a `driver`.

Because there are multiple methods to install [WeeWX V5](https://weewx.com/docs/5.0/usersguide/installing/) and
[WeeWX V4](http://weewx.com/docs/4.10/usersguide.htm#installing), location of files can vary.
For [WeeWX V5 see](https://weewx.com/docs/5.0/usersguide/where/) and
for [WeeWX V4 see](http://weewx.com/docs/4.10/usersguide.htm#Where_to_find_things) for the definitive information.
The following symbolic names are used to define the various locations:

* *BIN_DIR*       - The directory containing the WeeWX executables.
* *$CONFIG_DIR*   - The directory where the configuration (typically, weewx.conf) is located.
* *$DOWNLOAD_DIR* - The directory containing the downloaded *MQTTSubscribe* extension.
* *EXTENSION_DIR* - The directory containing the WeeWX extension, MQTTSubscribe.

The notation vX.Y.Z designates the version of MQTTSubscribe being installed.

Prior to making any updates/changes, always make a backup.

## Prerequisites

* Python 3.7 or higher
* [Paho MQTT Python client](https://pypi.org/project/paho-mqtt/)

## Installing with WeeWX Version 5.x

1. Setup
    Set the download directory.

    ```
    DOWNLOAD_DIR=/tmp
    ```

    For a pip install, set the extension directory, the configuration file, and activate the environment.

    ```
    EXTENSION_DIR=~/weewx-data/bin/user
    BIN_DIR=~/weewx-data/bin
    source ~/weewx-venv/bin/activate
    ```

    For a package install, set the extension directory and the configuration file,

2. Download MQTTSubscribe

    ```bash
    wget -P $DOWNLOAD_DIR https://github.com/bellrichm/WeeWX-MQTTSubscribe/archive/vX.Y.Z.tar.gz
    ```

    All of the releases can be found [here](https://github.com/bellrichm/WeeWX-MQTTSubscribe/releases) and this is the [latest](https://github.com/bellrichm/WeeWX-MQTTSubscribe/releases/latest).

3. Install MQTTSubscribe
        ```
        weectl extension install $DOWNLOAD_DIR/vX.Y.Z.tar.gz
        ```
4. Create an example `mqttsubscribe.template.conf`

    ```
    python3 $EXTENSION_DIR/MQTTSubscribe.py configure --create-example mqttsubscribe.template.conf
    ```

5. Edit the `mqttsubscribe.template.conf` file

6. Validate the `mqttsubscribe.template.conf` file

    If running as a driver,

    ```
    python3 $EXTENSION_DIR/MQTTSubscribe.py configure driver --validate mqttsubscribe.template.conf
    ```

7. Run in simulation mode

    If running as a driver,

    ```
    PYTHONPATH=$BIN_DIR python3 $EXTENSION_DIR/MQTTSubscribe.py simulate driver --conf mqttsubscribe.template.conf
    ```

### WeeWX Version 5.x Package Install

### WeeWX Version 5.x pip Install

## Installing with WeeWX Version 4.x

### WeeWX Version 4.x Package Install

### WeeWX Version 4.x setup.py Install

## Debugging

See, [debugging](https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/Debugging).

## Getting Help

Feel free to [open an issue](https://github.com/bellrichm/WeeWX-MQTTSubscribe/issues/new),
[start a discussion in github](https://github.com/bellrichm/WeeWX-MQTTSubscribe/discussions/new),
or [post on WeeWX google group](https://groups.google.com/g/weewx-user).
When doing so, see [Help! Posting to weewx user](https://github.com/weewx/weewx/wiki/Help!-Posting-to-weewx-user)
for information on capturing the log.
And yes, **capturing the log from WeeWX startup** makes debugging much easeier.

[![Build status](https://ci.appveyor.com/api/projects/status/r0e08p7qt278thax?svg=true)](https://ci.appveyor.com/project/bellrichm/weewx-mqttsubscribe-master)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=alert_status)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)

[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=bugs)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=code_smells)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=coverage)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=duplicated_lines_density)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=ncloc)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=security_rating)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=sqale_index)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=bellrichm_WeeWX-MQTTSubscribe&metric=vulnerabilities)](https://sonarcloud.io/dashboard?id=bellrichm_WeeWX-MQTTSubscribe)

[![codecov](https://codecov.io/gh/bellrichm/WeeWX-MQTTSubscribe/branch/master/graph/badge.svg)](https://codecov.io/gh/bellrichm/WeeWX-MQTTSubscribe)

[![Coverage Status](https://coveralls.io/repos/github/bellrichm/WeeWX-MQTTSubscribe/badge.svg?branch=master&service=github)](https://coveralls.io/github/bellrichm/WeeWX-MQTTSubscribe?branch=master)
