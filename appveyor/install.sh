#
#    Copyright (c) 2020-2021 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
    # set
    if [ "$ENABLED" != "true" ]; then
      exit 0
    fi

    if [ "$SONAR_UPLOAD" = "true" ]; then
      echo "Running sonar runner install"
      curl --create-dirs -sSLo $HOME/.sonar/sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SONAR_SCANNER_VERSION-linux.zip
      unzip -qq -o $HOME/.sonar/sonar-scanner.zip -d $HOME/.sonar/
    fi

    echo "Running mosquitto install"
    sudo apt-get -qq --assume-yes install mosquitto

    echo "Running pip installs"
    pip install configobj --quiet --no-python-version-warning
    pip install paho-mqtt --quiet --no-python-version-warning
    pip install mock --quiet --no-python-version-warning
    pip install pylint --quiet --no-python-version-warning
    pip install pytest --quiet --no-python-version-warning
    pip install pytest-cov --quiet --no-python-version-warning
    pip install coveralls --quiet --no-python-version-warning
    #pip install nose --quiet --no-python-version-warning
    #pip install coverage --quiet --no-python-version-warning

    echo "Running weewx install"
    if [ "$WEEWX" = "master" ]; then
      git clone https://github.com/weewx/weewx.git weewx
      cd weewx
      git show --oneline -s | tee master.txt
      detail=`cat master.txt`
      appveyor AddMessage "Testing against master " -Category Information -Details "$detail"
    elif [ "$WEEWX" = "development" ]; then
      git clone https://github.com/weewx/weewx.git weewx
      cd weewx
      git checkout development
      git show --oneline -s | tee development.txt
      detail=`cat development.txt`
      appveyor AddMessage "Testing against development " -Category Information -Details "$detail"      
    else
      wget  $WEEWX_URL/weewx-$WEEWX.tar.gz
      mkdir weewx
      tar xfz weewx-$WEEWX.tar.gz --strip-components=1 -C weewx
    fi
