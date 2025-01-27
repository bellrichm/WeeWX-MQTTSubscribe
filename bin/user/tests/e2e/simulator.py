#
#    Copyright (c) 2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
''' 
Simulator to be used when testing WeeWX/MQTTSubscribe
For more information on what could be done see, 
'''

import weewx.drivers.simulator
import weewx.engine

DRIVER_NAME = 'Simulator'

def loader(config_dict, engine):
    '''Load and return the driver. '''
    station = Simulator(engine, config_dict)
    return station

class Simulator(weewx.drivers.simulator.Simulator, weewx.engine.StdService):
    ''' A simulator driver to be used when testing WeeWX/MQTTSubscribe.'''
    # (methods not used) pylint: disable=abstract-method
    def __init__(self, engine, config_dict):
        start_ts, resume_ts = weewx.drivers.simulator.extract_starts(config_dict, DRIVER_NAME)
        stn_dict = config_dict[DRIVER_NAME]
        weewx.drivers.simulator.Simulator.__init__(self, start_time=start_ts, resume_time=resume_ts, **stn_dict)

        weewx.engine.StdService.__init__(self, engine, config_dict)

        self.engine = engine
        self.max_archive_records = stn_dict.get('max_archive_records', 2)
        self.max_archive_records = stn_dict.get('max_archive_records', 0)
        self.count_archive_records = 0

        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        self.bind(weewx.END_ARCHIVE_PERIOD, self.end_archive_period)

    def new_archive_record(self, event):
        ''' Handle the new archive record event.'''
        print(event.record)

    def end_archive_period(self, _event):
        ''' Handle the end of the archive period. '''
        self.count_archive_records +=1
        if self.count_archive_records > self.max_archive_records:
            #self.engine.shutDown()
            raise Exception("Max archive records has been achieved.")
