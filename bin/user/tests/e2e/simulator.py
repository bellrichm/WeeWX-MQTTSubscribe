#
#    Copyright (c) 2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
''' 
Simulator to be used when testing WeeWX/MQTTSubscribe
For more information on what could be done see, https://groups.google.com/g/weewx-user/c/pLnIps7dIZU/m/KtlAdSgWCAAJ
'''

import weewx.drivers.simulator
import weewx.engine

import weeutil
from weeutil.weeutil import to_int, to_list, to_sorted_string

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

        self.max_archive_records = to_int(stn_dict.get('max_archive_records', 1))
        self.remove_fields_from_archive_record = to_list(stn_dict.get('remove_fields_from_archive_record', []))

        self.count_archive_records = 0
        self.count_loop_packets = 0

        self.bind(weewx.NEW_LOOP_PACKET, self.new_loop_packet)
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)
        self.bind(weewx.PRE_LOOP, self.pre_loop)

    def pre_loop(self, _event):
        ''' Handle the pre_loop event. '''
        self.count_archive_records +=1
        if self.count_archive_records > self.max_archive_records:
            #self.engine.shutDown()
            raise Exception("Max archive records has been achieved.")

    def new_loop_packet(self, _event):
        ''' Handle the new loop packet event. '''
        self.count_loop_packets +=1

    def new_archive_record(self, event):
        ''' Handle the new archive record event.'''
        for field in self.remove_fields_from_archive_record:
            if field in event.record:
                del event.record[field]

        print("REC:   ",
              weeutil.weeutil.timestamp_to_string(event.record['dateTime']),
              to_sorted_string(event.record))
