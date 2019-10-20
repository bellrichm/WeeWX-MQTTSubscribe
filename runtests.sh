PYTHON=python2
WEEWX=weewx_3.9.2

PYTHONPATH=bin:../$WEEWX/bin $PYTHON -m unittest discover bin/user/tests