#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from env_init import *
from db_operator import *

def store():
    """
    存储数据
    """
    try:
        db_inst = MssqlConnection()
    except Exception:
        log_msg = 'Something wrong with the database when try transforing absolute time !!!'
        log_handler.error(log_msg)
        return FAI
    
    queue_len = len(sensor_data_queue)
    
    log_msg = 'queue length is : %d ' %queue_len
    log_handler.debug(log_msg)
    
    for _ in range(queue_len):
        try:
            sensor_data = sensor_data_queue.popleft()
        except IndexError:
            print 'nothing to pop here'
            return SUC
        room_id = sensor_data.room_id
        sense_time = sensor_data.time.timestamp
        log_msg = 'sensor_time = %s' %sense_time
        log_handler.debug(log_msg)
        
        try:
            instance_id = db_inst.insert_instance(room_id, sense_time)
            if instance_id == FAI or instance_id == ERR:
                continue
        
            db_inst.connect()
            for one_data in sensor_data.sensor:
                sql_str = 'insert into tb_data(instance_id, sensor_id, data) values(%d, %d, %f)' %(instance_id, one_data.id, one_data.value)
                db_inst.executeDML(sql_str)
            db_inst.close()
        except Exception, e:
            log_msg = 'Something wrong with the database when try transforing absolute time !!!'
            log_handler.error(log_msg)
            return FAI
    return SUC

def sensor_data_storage(stopEvent, param):
    """
    定时存储采集数据模块
    
    :param stopEvent: 模块停止事件
    :param param: 参数
    :rtype: 成功返回SUC，失败返回FAI，异常返回ERR
    """
    pointer = 0
    timer = Timer(THRESHOLD_LOAD_CYCLE, store)
    while not stopEvent.isSet():
        dbIsReady = MssqlConnection.test_connection()
        if dbIsReady == SUC:
            pointer = 0
            timer = Timer(DATA_STORING_CYCLE, store)
            timer.setName(THREAD_SENSOR_DATA_STORAGE)
            timer.start()
            while timer.isAlive():
                sleep(0.1)
        else:
            log_msg = 'Something wrong with the database, system will reconnect in %d seconds !!!' %db_reconnect_cycle[pointer]
            log_handler.error(log_msg)
            sleep(db_reconnect_cycle[pointer])
            pointer = (pointer + 1) % len(db_reconnect_cycle)
    timer.cancel()
    return SUC

if __name__ == '__main__':
    main_event = Event()
    try:
        sensor_data_storage(main_event, '')
    except KeyboardInterrupt:
        main_event.set()