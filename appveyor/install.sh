#
#    Copyright (c) 2020-2024 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
    # set
    if [ "$ENABLED" != "true" ]; then
      exit 0
    fi
    
    if [ "$MQTT_VERSION" != "" ]; then
      MQTT_INSTALL="=="$MQTT_VERSION
    fi

    if [ "$SONAR_UPLOAD" = "true" ]; then
      echo "Running sonar runner install"
      curl --create-dirs -sSLo $HOME/.sonar/sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SONAR_SCANNER_VERSION-linux.zip
      unzip -qq -o $HOME/.sonar/sonar-scanner.zip -d $HOME/.sonar/
    fi

    echo "Running mosquitto install"
    sudo apt-get -qq --assume-yes install mosquitto

    echo "Running pip installs"
    pip install pip --quiet --upgrade
    pip install configobj --quiet --no-python-version-warning
    pip install paho-mqtt$MQTT_INSTALL --quiet --no-python-version-warning
    pip install mock --quiet --no-python-version-warning
    pip install pylint --quiet --no-python-version-warning
    pip install pytest --quiet --no-python-version-warning
    pip install pytest-cov --quiet --no-python-version-warning
    pip install coveralls --quiet --no-python-version-warning

    echo "Running weewx install"
    if [ "$WEEWX" = "$BRANCH" ]; then
      git clone https://github.com/weewx/weewx.git weewx
      cd weewx
      git checkout $BRANCH
      git show --oneline -s | tee $BRANCH.txt
      detail=`cat $BRANCH.txt`
      appveyor AddMessage "Testing against $BRANCH " -Category Information -Details "$detail"
    elif [ "$WEEWX" = "4.6.1" ]; then
      wget  $WEEWX_URL/weewx-$WEEWX.tar.gz
      mkdir weewx
      tar xfz weewx-$WEEWX.tar.gz --strip-components=1 -C weewx    
    else
      wget  $WEEWX_URL/weewx-$WEEWX.tgz
      mkdir weewx
      tar xfz weewx-$WEEWX.tgz --strip-components=1 -C weewx
    fi
