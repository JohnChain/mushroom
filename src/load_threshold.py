#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from threading import Timer
from db_base import MssqlConnection

def load_threshold(stopEvent, param, ):
    """
    从数据库中载入环境限制范围

    :param param:
    :param stopEven:
    :rtype:
    """
    log_msg = 'Thread Load Threshold is Ready ...'
    log_handler.work(log_msg)
#     log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)

    db_inst = MssqlConnection()
    
    db_inst.transfor_absolute_time('2014-03-31 10:30:00.000')
    
    db_inst.connect()
    room_dupe = db_inst.queryAll('select distinct room_id from vw_task')
    room_list = []
    for i in room_dupe:
        room_list.append(i[0])
    db_inst.close()

    def load(room_id, threshold):
        temp = db_inst.get_threshold(room_id, threshold[room_id][1][1])
        if len(temp) == 2:
            threshold[room_id][0] = temp[0]
            threshold[room_id][1] = (temp[1][0],str(temp[1][1]))
        else:
            threshold[room_id][0] = temp[0]
            threshold[room_id][1] = (temp[0][0],str(temp[0][1]))
        
        log_msg = 'Load Threshold of Room_id : %d \n %s' %(room_id, str(threshold[room_id][0]))
        log_handler.work(log_msg)
#         log_msg = '[ Load Threshold ] Load Threshold of Room_id : %d ' %(room_id)
#         log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)
#         print log_msg
#         print threshold[room_id][0]
#         print threshold[room_id][1]
#         print '================================================'

    for room_id in room_list:
        if not threshold.has_key(room_id):
            threshold[room_id] = [(), (room_id, '1-1-1 1:1:1')]
            load(room_id, threshold)

    def timer_work():
        for room_id in room_list:
            if threshold[room_id][1][1] < str(datetime.now()):
                load(room_id, threshold)

    timer = Timer(THRESHOLD_LOAD_CYCLE, timer_work)
    timer.start()
    while not stopEvent.isSet():
        if timer.isAlive():
            sleep(0.1)
        else:
            timer = Timer(THRESHOLD_LOAD_CYCLE, timer_work)
            timer.start()
    timer.cancel()

    log_msg = 'Load Threshold Thread shutdown and cleaned! '
    log_handler.work(log_msg)
#     log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)

    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'

    exit()
if __name__ == '__main__':
    load_threshold('')
