# #! /usr/bin/python
# 
from head import *
from env_init import *
from db_operator import *

def store_data(sensor_data):
    try:
        db_inst = MssqlConnection()
    except Exception:
        log_msg = 'Something wrong with the database when try transforing absolute time !!!'
        log_handler.error(log_msg)
        return FAI
    
    room_id = sensor_data.room_id
    sense_time = sensor_data.time.timestamp
    log_msg = 'sensor_time = %s' %sense_time
    log_handler.debug(log_msg)
    
    try:
        instance_id = db_inst.insert_instance(room_id, sense_time)
        if instance_id == FAI:
            return FAI
    
        db_inst.connect()
        for one_data in sensor_data.sensor:
            
            sql_str = 'insert into tb_data(instance_id, sensor_id, data) values(%d, %d, %f)' %(instance_id, one_data.id, one_data.value)
            db_inst.executeDML(sql_str)
        db_inst.close()
    except Exception, e:
        log_msg = 'Something wrong with the database when try transforing absolute time !!!'
        log_handler.error(log_msg)
        return FAI