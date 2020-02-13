PYTHONPATH=bin:../weewx/bin pylint ./*.py
PYTHONPATH=bin:../weewx/bin pylint ./bin/user
PYTHONPATH=bin:../weewx/bin pylint ./bin/user/tests/unit/*.py -d duplicate-code
PYTHONPATH=bin:../weewx/bin pylint ./bin/user/tests/func/*.py -d duplicate-code