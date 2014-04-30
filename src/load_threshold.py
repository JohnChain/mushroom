#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from threading import Timer
from db_base import MssqlConnection

def load_threshold(stopEvent, param, ):
    """
    从数据库中载入环境限制范围

    :param stopEven:
    :param param:
    :rtype:
    """
    def load(room_id, threshold):
        str_time = threshold[room_id][1][1].strftime("%Y-%m-%d %H:%M:%S")
        temp = db_inst.get_threshold(room_id, str_time)
        log_msg = str(temp)
        log_handler.debug(log_msg)
        if len(temp) == 2:
            # 当前策略尚未执行完
            threshold[room_id][0] = temp[0]
            threshold[room_id][1] = (temp[1][0],temp[1][1])
            log_msg = 'Load Threshold of Room_id : %d \n%s' %(room_id, str(threshold[room_id][0]))
        elif len(temp) == 1:
            # 已执行至当前策略最后一条规则
            threshold[room_id][0] = temp[0]
            threshold[room_id][1] = (temp[0][0],temp[0][1])

            # 确保当前执行策略完整结束
            if temp[0][1] <= datetime.now():
                # 将该roomID所对应的policy_instance的状态设置为 OLD
                db_inst.update_policy_instance_state(room_id, POLICY_OLD)
                # 检查并载入当前房间的新执行策略
                db_inst.transfor_room_absolute_time(room_id)

            log_msg = 'Policy in Room [%d] Complete, Last Threshold : \n%s' %(room_id, str(threshold[room_id][0]))
            log_handler.debug(log_msg)
        else:
            # 当前房间无要新策略，均为就策略实例
            # 将该roomID所对应的policy_instance的状态设置为 OLD
            # 将该roomID从room2policy_instance字典中删除
            db_inst.update_policy_instance_state(room_id, POLICY_OLD)
            if db_inst.transfor_room_absolute_time(room_id) == FAI:
                # 此时后两种情况：1. 无新策略待执行； 2. 有新策略，但规则为空
                log_msg = 'There is no new policy in room %d currently' %room_id
                log_handler.debug(log_msg)
                return FAI
        log_handler.debug('[ROOM: %d] current threshold is : %s ' %(room_id, str(threshold)))

    def timer_work():
        for room_id in db_inst.room_dict.keys():
            try:
                if not threshold.has_key(room_id):
                    # 系统启动后首次载入环境限制
                    threshold[room_id] = [(), (room_id, datetime.now())]
                    load(room_id, threshold)
                elif threshold[room_id][1][1] < datetime.now():
                    load(room_id, threshold)
            except Exception, e:
                log_msg = 'Something wrong with the database when try loading threshold !!!'
                log_handler.error(log_msg)
                continue
    log_msg = 'Thread Load Threshold is Ready ...'
    log_handler.work(log_msg)

    try:
        db_inst = MssqlConnection()
        db_inst.transfor_absolute_time()
    except Exception:
        log_msg = 'Something wrong with the database when try transforing absolute time !!!'
        log_handler.error(log_msg)
        return ERR

    timer = Timer(THRESHOLD_LOAD_CYCLE, timer_work)
    timer.setName(THREAD_POLICY)
    timer.start()
    while not stopEvent.isSet():
        if timer.isAlive():
            sleep(0.1)
        else:
            timer = Timer(THRESHOLD_LOAD_CYCLE, timer_work)
            timer.setName(THREAD_POLICY)
            timer.start()
    timer.cancel()

    log_msg = 'Load Threshold Thread shutdown and cleaned! '
    log_handler.work(log_msg)
#     log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)

    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'

    exit()
if __name__ == '__main__':
    main_event = Event()
    try:
        load_threshold(main_event, '')
    except KeyboardInterrupt:
        main_event.set()

