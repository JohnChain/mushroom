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
    
    #TODO: translate 起始时间的选取
    db_inst.transfor_absolute_time('2014-03-31 10:30:00.000')
    
    db_inst.connect()
    room_dupe = db_inst.queryAll('select distinct room_id, policy_instance_id from vw_task')
    room2policy_instance = {}
    for i in room_dupe:
        room2policy_instance[i[0]] = i[1]
    db_inst.close()

    def load(room_id, threshold):
        temp = db_inst.get_threshold(room_id, threshold[room_id][1][1])
        if len(temp) == 2:
            threshold[room_id][0] = temp[0]
            threshold[room_id][1] = (temp[1][0],str(temp[1][1]))
            log_msg = 'Load Threshold of Room_id : %d \n%s' %(room_id, str(threshold[room_id][0]))
        elif len(temp) == 1:
            threshold[room_id][0] = temp[0]
            threshold[room_id][1] = (temp[0][0],str(temp[0][1]))
            # 将该roomID所对应的policy_instance的状态设置为 OLD
            db_inst.update_policy_instance_state(room2policy_instance[room_id], POLICY_OLD)
            log_msg = 'Policy in Room: %d Complete, Last Threshold : \n%s' %(room_id, str(threshold[room_id][0]))
        else:
            # 将该roomID所对应的policy_instance的状态设置为 OLD
            # 将该roomID从room2policy_instance字典中删除
            db_inst.update_policy_instance_state(room2policy_instance[room_id], POLICY_OLD)
            room2policy_instance.pop(room_id)
            log_msg = 'There is no new policy in room %d' %room_id
            pass
        log_handler.work(log_msg)

    # 系统启动后首次载入环境限制
    for room_id in room2policy_instance.keys():
        if not threshold.has_key(room_id):
            threshold[room_id] = [(), (room_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))]
            load(room_id, threshold)

    def timer_work():
        for room_id in room2policy_instance.keys():
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
