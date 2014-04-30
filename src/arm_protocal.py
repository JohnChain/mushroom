#!/usr/bin/env python
# -*- coding: utf-8 -*-

from head import *
from utils import *
from task_list import *
from db_operator import *
from mushroom_pb2 import *

def deal_read_time(proto_inst, fileno):
    """
    处理来自ARM的时间请求
    
    :param proto_inst: 半proto实例，header部分已反序列化，body部分未被反序列化
    :fileno: 当前套接字通信的连接句柄
    :rtype: 【待定】
    """
    header  = proto_inst['header_inst']
    data    = proto_inst['data']
    log_msg = 'From ARM READ_TIME -- '
    log_handler.communication(log_msg)

    one_task = Task()
    
    data = SynTime()
    data.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    version = proto_inst['header_inst'].version
    type    = 1 #TODO: 规定type类型
    message_header = gene_message_header(READ_TIME_RESPONSE, one_task.id, type, version, fileno, BIRTH_TYPE_AUTO)
    main_frame = gene_arm_frame(data = data, message_header = message_header)
    
    generate_task(one_task, main_frame, fileno, version, BIRTH_TYPE_AUTO)
    
    # log_msg = 'To ARM READ_TIME_RESPONSE -- taskID: %d, connection: %d, source: %d, version: %d, time: %s'\
                                        # %(one_task.id, fileno, one_task.birth_type, version, data.timestamp)
    log_msg = 'To ARM READ_TIME_RESPONSE -- \n%s' %b2a_hex(main_frame)
    log_handler.communication(log_msg)

    log_msg = "length of task_list is %d" %len(global_task_list.task_list)
    log_handler.debug(log_msg)
    
#     update_time('', fileno)
    
    return SUC

def update_time(proto_inst, fileno):
    """
    更新ARM时间
    
    :param proto_inst: 半proto实例，header部分已反序列化，body部分未被反序列化
    :fileno: 当前套接字通信的连接句柄
    :rtype: 【待定】
    """
    one_task = Task()
    
    data = SynTime()
    data.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    version = A_VERSION
    type    = 1
    message_header = gene_message_header(UPDATE_TIME, one_task.id, type, version, fileno, BIRTH_TYPE_AUTO)

    log_msg = 'To ARM UPDATE_TIME -- taskID: %d, connection: %d, source: %d, version: %d, time: %s'\
                                %(one_task.id, fileno, BIRTH_TYPE_AUTO, version, data.timestamp)
    log_handler.communication(log_msg)


    main_frame = gene_arm_frame(data = data, message_header = message_header)
    
    log_msg = 'To ARM UPDATE_TIME -- \n%s' %b2a_hex(main_frame)
    log_handler.communication(log_msg)

    generate_task(one_task, main_frame, fileno, version, BIRTH_TYPE_AUTO)

def deal_update_time_response(proto_inst, fileno):
    """
    处理来自ARM的时间更新响应
    
    :param proto_inst: 半proto实例，header部分已反序列化，body部分未被反序列化
    :fileno: 当前套接字通信的连接句柄
    :rtype: 【待定】
    """
    response_code = ResponseCode()
    response_code.ParseFromString(proto_inst['data'])
    header_inst = proto_inst['header_inst']

    log_msg = 'From ARM UPDATE_TIME_RESPONSE -- '
    log_handler.communication(log_msg)

    #TODO: 这里将分析header内的birth_type和fileno,发向相应的套接字
    result = SUC
    if header_inst.source == BIRTH_TYPE_AUTO:
        if response_code.code == OK:
            log_msg = "From ARM UPDATE_TIME_RESPONSE -- update time succeed"
        else:
            log_msg = "From ARM UPDATE_TIME_RESPONSE -- update time failed, error log : %s" %response_code.log
            result = FAI
    else:
        result = ERR
    
    log_handler.communication(log_msg)
    
    return result

#===================================================================================

def deal_read_conf(proto_inst, fileno):
    """
    处理来自ARM的配置读取请求
    
    :param proto_inst: 半proto实例，header部分已反序列化，body部分未被反序列化
    :fileno: 当前套接字通信的连接句柄
    :rtype: 【待定】
    """
    temp_data = ConfigList()
    temp_data.ParseFromString(proto_inst['data'])
    
    response_list = ConfigList()
    for i in temp_data.config:
        one_config = response_list.config.add()
    
    
def update_conf(proto_inst, fileno):
    """
    更新ARM配置
    
    :param proto_inst: 半proto实例，header部分已反序列化，body部分未被反序列化
    :fileno: 当前套接字通信的连接句柄
    :rtype: 【待定】
    """
    pass

def deal_update_conf_response(proto_inst, fileno):
    """
    处理来自ARM的配置更新响应
    
    :param proto_inst: 半proto实例，header部分已反序列化，body部分未被反序列化
    :fileno: 当前套接字通信的连接句柄
    :rtype: 【待定】
    """
    response_code = ResponseCode()
    response_code.ParseFromString(proto_inst['data'])
    if response_code.code == OK:
        print "update time succeed"
    else:
        print "update time failed, error log : %s" %response_code.log

# ===================================================================================

def read_controller_state(controller_id, fileno):
    """
    查看控制状态
    
    :param proto_inst: 半proto实例，header部分已反序列化，body部分未被反序列化
    :fileno: 当前套接字通信的连接句柄
    :rtype: 【待定】
    """
    one_task = Task()
    
    data = Controller()
    data.controller_id = controller_id
    
    version = A_VERSION
    type    = 1
    message_header = gene_message_header(READ_CONTROLLER_STATE, one_task.id, type, version, fileno, BIRTH_TYPE_AUTO)
    main_frame = gene_arm_frame(data = data, message_header = message_header)
    
    log_msg = 'To ARM READ_CONTROLLER_STATE -- \n%s' %b2a_hex(main_frame)
    log_handler.communication(log_msg)

    generate_task(one_task, main_frame, fileno, version, BIRTH_TYPE_AUTO)

def deal_read_controller_state_response(proto_inst, fileno):
    """
    处理来自ARM的查看控制器状态响应
    
    :param proto_inst: 半proto实例，header部分已反序列化，body部分未被反序列化
    :fileno: 当前套接字通信的连接句柄
    :rtype: 【待定】
    """
    proto_data = Controller()
    proto_data.ParseFromString(proto_inst['data'])
    header_inst = proto_inst['header_inst']

    log_msg = 'From ARM READ_CONTROLLER_STATE_RESPONSE -- '
    log_handler.communication(log_msg)

    #TODO: 这里将分析header内的birth_type和fileno,发向相应的套接字
    if header_inst.source == BIRTH_TYPE_AUTO:
        db_inst = DbOperator()
        db_inst.update_controller(proto_data.controller_id, proto_data.state)
    else:
        dj_node = django_client_dic[header_inst.connection]
        #TODO: 构造Json格式，发送
        json_inst = {'uri': 'device/viewer',
                     'type': 'response',
                     'data': {
                              'roomId': 1,
                              'controllerId': proto_data.controller_id,
                              'state': proto_data.state,
                              }
                    }
        head = D_HEAD
        version = D_VERSION  #TODO:版本统一 
        message_to_dj = gene_django_frame(head, version, json_inst)
        dj_node.handler.send(message_to_dj)

        log_msg = 'To django view device response -- head: %s, version: %d, data: %s' %(head, version, json.dumps(json_inst))
        log_handler.communication(log_msg)
    
    return SUC
        
def update_controller_state(controller_id, state, fileno):
    """
    更新控制器
    
    :param controller_id: 控制器ID
    :param state: 设置控制器状态
    :fileno: 当前套接字通信的连接句柄
    :rtype: 【待定】
    """
    one_task = Task()
    
    data = Controller()
    data.controller_id = controller_id
    data.state = state
    
    version = A_VERSION
    type    = 1
    message_header = gene_message_header(UPDATE_CONTROLLER_STATE, one_task.id, type, version, fileno, BIRTH_TYPE_AUTO)
    main_frame = gene_arm_frame(data = data, message_header = message_header)
    
    log_msg1 = 'To ARM UPDATE_CONTROLLER_STATE -- taskID: %d, connection: %d, source: %d version: %d, controller_id: %d, state: %d \n' \
                                                            %(one_task.id, fileno, BIRTH_TYPE_AUTO, version, controller_id, state)
    log_handler.communication(log_msg1)
    log_msg2 = '%s' %b2a_hex(main_frame)
    log_handler.communication(log_msg1 + log_msg2)

    generate_task(one_task, main_frame, fileno, version, BIRTH_TYPE_AUTO)
    
def deal_update_controller_state_response(proto_inst, fileno):
    """
    处理来自ARM的控制器更新响应
    
    :param proto_inst: 半proto实例，header部分已反序列化，body部分未被反序列化
    :fileno: 当前套接字通信的连接句柄
    :rtype: 【待定】
    """
    response_code = ResponseCode()
    response_code.ParseFromString(proto_inst['data'])
    header_inst = proto_inst['header_inst']
    
    log_msg = 'From ARM UPDATE_CONTROLLER_STATE_RESPONSE -- '
    log_handler.communication(log_msg)

    result = SUC
    if header_inst.source == BIRTH_TYPE_AUTO:
        if response_code.code == OK:
            #TODO: 无法直接获知被成功更改的控制器ID 及更改后状态
#             db_inst = DbOperator()
#             db_inst.update_controller(response_code.controller_id, response_code.state)

            log_msg = "From ARM UPDATE_CONTROLLER_STATE_RESPONSE -- update  succeed"
            reslut = SUC        
        else:
            log_msg = "From ARM UPDATE_CONTROLLER_STATE_RESPONSE -- update failed, error log : %s" %response_code.log
            result = FAI
        log_handler.work(log_msg)
        return result
    else:
        try:
            dj_handler = django_client_dic[header_inst.connection]
        except KeyError, e:
            log_msg = 'In deal_update_controller_state_response: %s'%(str(e))
            log_handler.error(log_msg)
            return FAI
        json_inst = {'uri': 'device/controller',
                     'type': 'response',
                     'code': response_code.code,
                     'data': response_code.log,
                    }
        if response_code.code == 0:
            log_msg = "From ARM UPDATE_CONTROLLER_STATE_RESPONSE -- update  succeed"
            result  = SUC
        else:
            json_inst['code'] = -1
            json_inst['data'] = 'something wrong'
            result = FAI

            log_msg = "From ARM UPDATE_CONTROLLER_STATE_RESPONSE -- update failed, error log : %s" %response_code.log
        log_handler.communication(log_msg)
            
        head = D_HEAD
        version = D_VERSION  #TODO:版本统一 

        log_msg = 'To django UPDATE_CONTROLLER_STATE_RESPONSE -- head: %s, version: %s, body: %s' %(head, version, json.dumps(json_inst))
        log_handler.communication(log_msg)

        message_to_dj = gene_django_frame(head, version, json_inst)
        dj_handler.handler.send(message_to_dj)
        
        return result
    log_msg = 'header_inst.source not found'
    log_handler.debug(log_msg)
    return ERR   

# ===================================================================================

def read_sensor_data(room_id, fileno):
    one_task = Task()
    
    data = Room()
    data.room_id = room_id

    version = A_VERSION
    type    = 1
    message_header = gene_message_header(READ_SENSOR_DATA, one_task.id, type, version, fileno, BIRTH_TYPE_AUTO)
    main_frame = gene_arm_frame(message_header, data)
    
    log_msg = b2a_hex(main_frame)
    log_handler.communication('To ARM READ_SENSOR_DATA -- \n ' + log_msg)
    generate_task(one_task, main_frame, fileno, version, BIRTH_TYPE_AUTO)

def deal_read_sensor_data_response(proto_inst, fileno):
    sensor_data = SensorData()
    sensor_data.ParseFromString(proto_inst['data'])
    
    message_header = proto_inst['header_inst']

    log_msg = 'From ARM READ_SENSOR_DATA_RESPONSE -- '
    log_handler.communication(log_msg)
    
    room_id = sensor_data.room_id
    sense_time = sensor_data.time.timestamp
    log_msg = 'sensor_time = %s' %sense_time
    log_handler.debug(log_msg)
    
    data = {}
    try:
        db_inst = MssqlConnection()
        instance_id = db_inst.insert_instance(room_id, sense_time)
        
        if instance_id == FAI:
            return FAI
        
        db_inst.connect()
        for one_data in sensor_data.sensor:
            data[one_data.type] = one_data
            
            sql_str = 'insert into tb_data(instance_id, sensor_id, data) values(%d, %d, %f)' %(instance_id, one_data.id, one_data.value)
            db_inst.executeDML(sql_str)
        db_inst.close()
    except Exception, e:
        log_msg = 'Something wrong with the database when try transforing absolute time !!!'
        log_handler.error(log_msg)
        return FAI
    #TODO: 这里有个问题，每新建一个数据库实例时，会从数据库中load几张表，因为一下的insert_data函数用到了这些表，是否可以有更好的改进方法
#     db_inst.insert_data(room_id, sense_time, \
#                         data[TEMP].value, data[HUMI].value, data[CO2].value, data[LIGHT].value,\
#                         data[TEMP].id, data[HUMI].id, data[CO2].id, data[LIGHT].id )
    
    #TODO: 根据当前环境限制，发送响应控制器控制命令
    log_msg = ''
    if len(threshold) > 0 :
        try:
            if  data[TEMP].value < threshold[room_id][0][2]:
                log_msg = "it is too cold, please worm me up!"
                update_controller_state(1, ON, fileno)
            elif data[TEMP].value > threshold[room_id][0][3]:
                log_msg = 'it is too hot, please cool me down!'
                update_controller_state(2, OFF, fileno)
            else:
                log_msg = 'Hemperature is OK'
            log_handler.communication(log_msg)
            
            if  data[HUMI].value < threshold[room_id][0][4]:
                log_msg = 'it is too dry, please give me some water!'
                update_controller_state(3, ON, fileno)
            elif data[HUMI].value > threshold[room_id][0][5]:
                log_msg = 'it is too humid, please dry me up!'
                update_controller_state(4, OFF, fileno)
            else:
                log_msg = 'Humidity is OK'
            log_handler.communication(log_msg)
    
            if  data[CO2].value < threshold[room_id][0][6]:
                log_msg = 'it is co2-less, please give me some co2!'
                update_controller_state(5, ON, fileno)
            elif data[CO2].value > threshold[room_id][0][7]:
                log_msg = 'it is co2-ful, please give me some fresh air!'
                update_controller_state(6, OFF, fileno)
            else:
                log_msg = 'CO2 is OK'
            log_handler.communication(log_msg)
    
            if data[LIGHT].value < threshold[room_id][0][9]:
                log_msg = 'it is too bright, please dark me down !'
                update_controller_state(7, ON, fileno)
            elif data[LIGHT].value > threshold[room_id][0][10]:
                log_msg = 'it is too dark, please turn lights on !'
                update_controller_state(8, OFF, fileno)
            else:
                log_msg = 'brightness is OK'
        except KeyError:
            pass
        except IndexError:
            log_msg = 'No policy in Room: %d' %room_id
    else:
        log_msg = 'thresholds not ready yet'
    log_handler.work(log_msg)
def deal_sensor_data_push(proto_inst, fileno):
    #TODO: 同 deal_read_sensor_data_response
    pass

# ===================================================================================

def init_sync(proto_inst, fileno):
    """
    系统初始化，信息同步
    
    :param proto_inst: 半proto实例，header部分已反序列化，body部分未被反序列化
    :fileno: 当前套接字通信的连接句柄
    :rtype: 【待定】
    """
    conf_init = Init()
    conf_init.ParseFromString(proto_inst['data'])
    message_header = proto_inst['header_inst']

#     log_msg = str(conf_init)
#     log_handler.debug(log_msg)

    log_msg = 'From ARM INIT -- '
    log_handler.communication(log_msg)
    
    try:
        db_inst = MssqlConnection()
        
        for one_room in conf_init.roomconf:
            room_id = one_room.id
            if not db_inst.room_id2desc.has_key(room_id):
                db_inst.insert_room(room_id, 'Room_' + str(room_id))
                
            for one_sensor in one_room.sensor:
                sensor_id = one_sensor.id
                sensor_type = sensor_type_dict[one_sensor.type]
                if db_inst.sensor_id2name.has_key(sensor_id):
                    pass
                else:
                    db_inst.insert_sensor(sensor_id, sensor_type, room_id)
    #             room_dict['sensor'].append(sensor_id)
            
            for one_controller in one_room.controller:
                controller_id = one_controller.controller_id
                controller_type = controller_type_dict[one_controller.type]
                
                db_inst.insert_controller(controller_id, controller_type, room_id)
    #             room_dict['controller'].append(controller_id)
    except pyodbc.IntegrityError:
        pass
    except Exception, e:
        log_handler.error(str(e))
    for one_config in conf_init.config:
        key = one_config.key
        val = one_config.val
        
        sys_config_dict[key] = val
        
        log_msg = 'Here in init_sync key: %s value: %d' %(key, sys_config_dict[key])
        log_handler.debug(log_msg)
        
    return SUC

def reboot(fileno):
    """
    重启控制系统
    
    :fileno: 当前套接字通信的连接句柄
    :rtype: 【待定】
    """
    one_task = Task()
    
    version = A_VERSION
    type    = 1
    message_header = gene_message_header(REBOOT, one_task.id, type, version, fileno, BIRTH_TYPE_AUTO)
    main_frame = gene_arm_frame(data = '', message_header = message_header)
    
    generate_task(one_task, main_frame, fileno, version, BIRTH_TYPE_AUTO)
    
def deal_reboot_response(proto_inst, fileno):
    """
    处理来自ARM的重启响应
    
    :param proto_inst: 半proto实例，header部分已反序列化，body部分未被反序列化
    :fileno: 当前套接字通信的连接句柄
    :rtype: 【待定】
    """
    response_code = ResponseCode()
    response_code.ParseFromString(proto_inst['data'])
    header_inst = proto_inst['header_inst']
    log_msg = ''
    if header_inst.source == BIRTH_TYPE_AUTO:
        if response_code.code == OK:
            log_msg = "reboot successfully"
        else:
            log_msg = "reboot failed, error log : %s" %response_code.log
    else:
        if response_code.code == OK:
            log_msg = "reboot successfully"
        else:
            log_msg = "reboot failed, error log : %s" %response_code.log
    log_handler.communication(log_msg)
# ===================================================================================
arm_protocal = {
    READ_TIME : deal_read_time,
    UPDATE_TIME : update_time,
    UPDATE_TIME_RESPONSE : deal_update_time_response,

    READ_CONF : deal_read_conf,
#     READ_CONF_RESPONSE : deal_read_conf_response,
    UPDATE_CONF : update_conf,
    UPDATE_CONF_RESPONSE : deal_update_conf_response,
    REBOOT: reboot,
    REBOOT_RESPONSE : deal_reboot_response,
    
    READ_CONTROLLER_STATE : read_controller_state,
    READ_CONTROLLER_STATE_RESPONSE : deal_read_controller_state_response,
    UPDATE_CONTROLLER_STATE : update_controller_state,
    UPDATE_CONTROLLER_STATE_RESPONSE : deal_update_controller_state_response,
    
    READ_SENSOR_DATA : read_sensor_data,
    READ_SENSOR_DATA_RESPONSE : deal_read_sensor_data_response,
    SENSOR_DATA_PUSH: deal_read_sensor_data_response,
    
    INIT : init_sync,
}
