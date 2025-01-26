#
#    Copyright (c) 2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
''' Simulator to be used when testing WeeWX/MQTTSubscribe'''

import weewx.drivers.simulator

DRIVER_NAME = 'Simulator'

# See, for more information on what could be done.

def loader(config_dict, _engine):
    '''Load and return the driver. '''
    start_ts, resume_ts = weewx.drivers.simulator.extract_starts(config_dict, DRIVER_NAME)
    station = Simulator(start_time=start_ts, resume_time=resume_ts, **config_dict[DRIVER_NAME])
    return station

class Simulator(weewx.drivers.simulator.Simulator):
    ''' A simulator driver to be used when testing WeeWX/MQTTSubscribe.'''
    # (methods not used) pylint: disable=abstract-method
    def __init__(self, **stn_dict):
        super().__init__(**stn_dict)
