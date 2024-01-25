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

**To install version 3.x with WeeWX 4.x see,
[Installing and updating version 3.x with WeeWX 4.x](https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/Installing-and-updating-version-3.x--with-WeeWX-4.x)**

**Note:** It is rare that MQTTSubscribe should be configured to run as both a `service` and `driver`.
If you are augmenting an existing driver's data, run MQTTSubscribe as a `service`. Otherwise, run it as a `driver`.

Because there are multiple methods to install [WeeWX V5](https://weewx.com/docs/5.0/usersguide/installing/), location of files can vary.
[See](https://weewx.com/docs/5.0/usersguide/where/) for the definitive information.
The following symbolic names are used to define the various locations:

* *$WEEWX_REPO*  - For git 'installs', the location of the repository (This is not typically in the WEEWX documentation)
* *$WEEWX_ROOT*  - WeeWX root directory
* *$BIN_ROOT*    - Executables
* *$USER_ROOT*   - User directory
* *$CONFIG_FILE* - The WeeWX configuration file (This is not typically in the WEEWX documentation)
* *$WEECTL*      - The `weectl` program (This is not typically in the WEEWX documentation)

The notation vX.Y.Z designates the version of MQTTSubscribe being installed.

**Prior to making any updates/changes, always make a backup.**

## Prerequisites

* Python 3.7 or higher
* [Paho MQTT Python client](https://pypi.org/project/paho-mqtt/)

## Initial installation

### Set the mode that MQTTSubscribe will be running in

If running as a driver,

```
RUN_MODE=driver
```

If running as a service,

```
RUN_MODE=service
```

### For pip and git installs - activate the environment

```
source ~/weewx-venv/bin/activate
```

### Set the file locations

#### For pip installs

```
WEEWX_ROOT=~/weewx-data
export USER_ROOT=$WEEWX_ROOT/bin/user
CONFIG_FILE=$WEEWX_ROOT/weewx.conf
WEECTL=weectl
```

#### For package installs

```
WEEWX_ROOT=/etc/weewx/
export BIN_ROOT=/usr/share/weewx/
export USER_ROOT=$WEEWX_ROOT/bin/user
CONFIG_FILE=$WEEWX_ROOT/weewx.conf
WEECTL=weectl
```

#### For git 'installs'

```
WEEWX_REPO=~/weewx
WEEWX_ROOT=~/weewx-data
export BIN_ROOT=$WEEWX_REPO/src
export USER_ROOT=$WEEWX_ROOT/bin/user
CONFIG_FILE=$WEEWX_ROOT/weewx.conf
WEECTL=$WEEWX_REPO/bin/weectl
```

### Install MQTTSubscribe

```
$WEECTL extension install https://github.com/bellrichm/WeeWX-MQTTSubscribe/archive/refs/tags/latest.zip
```

**Note:** For package installs, the above command needs to be prefixed with `sudo` (sudo $WEECTL ...)

### Create an example configuration

```
python3 $USER_ROOT/MQTTSubscribe.py configure --create-example mqttsubscribe.template.conf
```

### Configure MQTTSubscribe

Note, MQTTSubscribeDriver can also be configured and weewx.conf updated interactively via
[weectl station](https://weewx.com/docs/5.0/utilities/weectl-about/). This method has the following disadvantages:

* The options that can be configured are limited.
* The configuration options can not be validated and tested before restarting WeeWX.

1. Edit the `mqttsubscribe.template.conf` file

    For example,

    ```
    nano mqttsubscribe.template.conf
    ```

2. Validate and test the `mqttsubscribe.template.conf` file

    ```
    python3 $USER_ROOT/MQTTSubscribe.py configure $RUN_MODE --validate --conf mqttsubscribe.template.conf
    ```

    ```
    python3 $USER_ROOT/MQTTSubscribe.py simulate $RUN_MODE --conf mqttsubscribe.template.conf
    ```

  Additional information on running MQTTSubscribe in configuration mode can be found at this [wiki page](https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/MQTTSubscribe-Configurator-Mode).
  
  Additional information on running MQTTSubscribe in simulation mode can be found at this [wiki page](https://github.com/bellrichm/WeeWX-MQTTSubscribe/wiki/MQTTSubscribe-Simulator-mode).

### If running as a driver, set driver to MQTTSubscribe

```
$WEECTL station reconfigure --driver=user.MQTTSubscribe --no-prompt
```

**Note:** For package installs, the above command needs to be prefixed with `sudo` (sudo $WEECTL ...)

### If running as a service, enable it

```
python3 $USER_ROOT/MQTTSubscribe.py configure service --enable true --conf mqttsubscribe.template.conf
```

### Update WeeWX with MQTTSubscribe's configuration

1. Update weewx.conf

    ```
    python3 $USER_ROOT/MQTTSubscribe.py configure $RUN_MODE --replace-with mqttsubscribe.template.conf --conf $CONFIG_FILE
    ```

    **Note:** For package installs, the above command needs to be prefixed with `sudo -E` (sudo -E $python3 ...)

2. Restart WeeWX

## Updating MQTTSubscribe

1. If pip or git install, [activate the environment](https://github.com/bellrichm/WeeWX-MQTTSubscribe#for-pip-and-git-installs---activate-the-environment).
2. [Set the file locations](https://github.com/bellrichm/WeeWX-MQTTSubscribe#set-the-file-locations) for the method used to install WeeWX.
3. Follow the steps to [install MQTTSubscribe](https://github.com/bellrichm/WeeWX-MQTTSubscribe#install-mqttsubscribe).
4. Restart WeeWX.

## Reconfiguring MQTTSubscribe

1. If pip or git install, [activate the environment](https://github.com/bellrichm/WeeWX-MQTTSubscribe#for-pip-and-git-installs---activate-the-environment).
2. [Set the file locations](https://github.com/bellrichm/WeeWX-MQTTSubscribe#set-the-file-locations) for the method used to install WeeWX.
3. Export the current configuration settings.

    ```
    python3 $USER_ROOT/MQTTSubscribe.py configure $RUN_MODE --export mqttsubscribe.template.conf --conf $CONFIG_FILE
    ```

4. Follow the diections to
    * [Configure MQTTSunscribe](https://github.com/bellrichm/WeeWX-MQTTSubscribe#configure-mqttsubscribe)
    * [Update WeeWX](https://github.com/bellrichm/WeeWX-MQTTSubscribe#update-weewx-with-mqttsubscribes-configuration)

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
