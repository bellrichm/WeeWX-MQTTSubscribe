    #export SONAR_SCANNER_VERSION=4.2.0.1873
    #export SONAR_SCANNER_HOME=$HOME/.sonar/sonar-scanner-$SONAR_SCANNER_VERSION-linux
    echo "Running sonar runner install"
    curl --create-dirs -sSLo $HOME/.sonar/sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SONAR_SCANNER_VERSION-linux.zip
    unzip -qq -o $HOME/.sonar/sonar-scanner.zip -d $HOME/.sonar/
    #export PATH=$SONAR_SCANNER_HOME/bin:$PATH
    export SONAR_SCANNER_OPTS="-server"
    echo $PATH

    echo "Running mosquitto install"
    sudo apt-get -qq --assume-yes install mosquitto

    echo "Running pip installs"
    pip install configobj --quiet --no-python-version-warning
    pip install paho-mqtt --quiet --no-python-version-warning
    pip install mock --quiet --no-python-version-warning
    pip install pylint --quiet --no-python-version-warning
    pip install coveralls --quiet --no-python-version-warning
    pip install nose --quiet --no-python-version-warning
    pip install coverage --quiet --no-python-version-warning

    echo "Running weewx install"
    wget  $WEEWX_URL/$WEEWX
    mkdir weewx
    tar xfz $WEEWX --strip-components=1 -C weewx    