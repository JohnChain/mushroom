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
    one_task = Task()
    
    data = SynTime()
    data.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    version = proto_inst['header_inst'].version
    type    = 1 #TODO: 规定type类型
    message_header = gene_message_header(READ_TIME_RESPONSE, one_task.id, type, version, fileno, BIRTH_TYPE_AUTO)
    main_frame = gene_arm_frame(data = data, message_header = message_header)
    
    generate_task(one_task, main_frame, fileno, version, BIRTH_TYPE_AUTO)
    print '\n here in task_list' , fileno, one_task.frame, one_task.birth_type, '<<<<<<<'
    print "length of task_list is %d" %len(global_task_list.task_list)

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
    message_header = gene_message_header(UPDATE_TIME_RESPONSE, one_task.id, type, version, fileno, BIRTH_TYPE_AUTO)
    main_frame = gene_arm_frame(data = data, message_header = message_header)
    
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
    #TODO: 这里将分析header内的birth_type和fileno,发向相应的套接字
    if header_inst.source == BIRTH_TYPE_AUTO:
        if response_code.code == OK:
            print "update time succeed"
        else:
            print "update time failed, error log : %s" %response_code.log
    else:
        pass
    
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
    if header_inst.source == BIRTH_TYPE_AUTO:
        if response_code.code == OK:
            print "update time succeed"
        else:
            print "update time failed, error log : %s" %response_code.log
    else:
        #TODO: 后期前台可以添加功能
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
    #TODO: 这里将分析header内的birth_type和fileno,发向相应的套接字
    if header_inst.source == BIRTH_TYPE_AUTO:
        db_inst = DbOperator()
        db_inst.update_controller(proto_data.controller_id, proto_data.state)
        return 1
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
        return 1
        
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
    if header_inst.source == BIRTH_TYPE_AUTO:
        if response_code.code == OK:
            print "update time succeed"
            db_inst = DbOperator()
            db_inst.update_controller(proto_inst.controller_id, proto_inst.state)
            return 1
        else:
            print "update time failed, error log : %s" %response_code.log
            return 0
    else:
        try:
            dj_handler = django_client_dic[header_inst.connection]
        except KeyError:
            return 0
        #TODO: 构造Json格式，发送
        json_inst = {'uri': 'device/controller',
                     'type': 'response',
                     'code': response_code.code,
                     'data': response_code.log,
                    }
        if response_code.code == 0:
            print "update time succeed"
        else:
            print "update time failed, error log : %s" %response_code.log
            json_inst['code'] = -1
            json_inst['data'] = 'something wrong'
        
        head = D_HEAD
        version = D_VERSION  #TODO:版本统一 
        message_to_dj = gene_django_frame(head, version, json_inst)
        dj_handler.handler.send(message_to_dj)
        return 1
# ===================================================================================
def read_sensor_data(room_id, fileno):
    one_task = Task()
    
    data = Room()
    data.room_id = room_id

    version = A_VERSION
    type    = 1
    message_header = gene_message_header(READ_SENSOR_DATA, one_task.id, type, version, fileno, BIRTH_TYPE_AUTO)
    main_frame = gene_arm_frame(message_header, data)
    
    generate_task(one_task, main_frame, fileno, version, BIRTH_TYPE_AUTO)

def deal_read_sensor_data_response(proto_inst, fileno):
    sensor_data = SensorData()
    sensor_data.ParseFromString(proto_inst['data'])
    
    room_id = sensor_data.room.room_id
    sensor_time = sensor_data.time.timestamp
    data = {}
    for one_data in sensor_data.sensor:
        data[one_data.type] = one_data
    
    db_inst = MssqlConnection()
    #TODO: 这里有个问题，每新建一个数据库实例时，会从数据库中load几张表，因为一下的insert_data函数用到了这些表，是否可以有更好的改进方法
    db_inst.insert_data(room_id, sensor_time, \
                        data[TEMP].value, data[HUMI].value, data[CO2].value, data[LIGHT].value,\
                        data[TEMP].id, data[HUMI].id, data[CO2].id, data[LIGHT].id )
    
    if len(threshold) > 0 :
        if  data[TEMP].value < threshold[room_id][0][2]:
            print "it is too cold, please worm me up!"
#             update_controller_state(db_inst.controller_dict[sensor_data.room][0], 1, fileno)
            #TODO: 
        elif data[TEMP].value > threshold[room_id][0][3]:
            print 'it is too hot, please cool me down!'
        if  data[HUMI].value < threshold[room_id][0][4]:
            print 'it is too dry, please give me some water!'
        elif data[HUMI].value > threshold[room_id][0][5]:
            print 'it is too humid, please dry me up!'
        if  data[CO2].value < threshold[room_id][0][6]:
            print 'it is co2-less, please give me some co2!'
        elif data[CO2].value > threshold[room_id][0][7]:
            print 'it is co2-ful, please give me some fresh air!'
        if data[LIGHT].value != threshold[room_id][0][8]:
            print 'it is time to change light to %s' %(threshold[room_id][0][8])
    
    read_sensor_data(room_id, fileno)
    
def deal_sensor_data_push(proto_inst, fileno):
    #TODO: 同 deal_read_sensor_data_response
    pass 

# ===================================================================================

arm_protocal = {
    READ_TIME : deal_read_time,
#     READ_TIME_RESPONSE : deal_read_time_response,
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
#     SENSOR_DATA_PUSH: deal_sensor_data_push,
    SENSOR_DATA_PUSH: deal_read_sensor_data_response,
}
