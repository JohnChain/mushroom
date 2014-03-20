#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from task_list import *
from mushroom_pb2 import *
from utils import *

def device_controller(json_inst, client_handler):
    """
    发送控制命令的数据包
    
    :param json_inst: jeon 格式的对象
    :clent_handler: TCP连接句柄
    :rtype: 1 无误， 0 有误 
    """
    print 'in device_controller_req...'
    
    one_task = Task()
    version = A_VERSION
    type    = 1
    message_header = gene_message_header(UPDATE_CONTROLLER_STATE, one_task.id, type, version, client_handler.fileno(), BIRTH_TYPE_MANUAL)
    
    data = Controller()
    data.controller_id = int(json_inst['data']['controllerId'])
    #TODO: 'on'/'off' 全局标记
    if json_inst['data']['action'] == 'on':
        data.state = Controller.OPEN
    else:
        data.state = Controller.CLOSE
#     data.room.room_id = json_inst['data']['roomId']
    version = 1
    main_frame = gene_arm_frame(message_header = message_header, data = data, )
    
    generate_task(one_task, main_frame, client_handler.fileno(), version, BIRTH_TYPE_MANUAL)
    return 1
    
def device_viewer(json_inst, client_handler):
    """
    查看设备的运行状态
    
    :param json_inst: jeon 格式的对象
    :clent_handler: TCP连接句柄
    :rtype: 1 无误， 0 有误 
    """
    print 'in device_viewer_req...'
    one_task = Task()
    version = A_VERSION
    type    = 1
    message_header = gene_message_header(READ_CONTROLLER_STATE, one_task.id, type, version, client_handler.fileno(), BIRTH_TYPE_MANUAL)
    
    data = Controller()
    data.controller_id = int(json_inst['data']['controllerId'])
#     data.room.room_id = json_inst['data']['roomId']
    
    main_frame = gene_arm_frame(data = data, message_header = message_header)
    
    generate_task(one_task, main_frame, client_handler.fileno(), version, BIRTH_TYPE_MANUAL)
    return 1

def log_view(json_inst, client_handler):
    """
    控制设备
    
    :param json_inst: jeon 格式的对象
    :clent_handler: TCP连接句柄
    :rtype: 1 无误， 0 有误 
    """
    print 'in log view'
    log_inst = log_manager.view_record(json_inst['type'])
    
    response = {'uri': 'log',
                'type': 'response',
                }
    if log_inst != '': 
        response['code'] = 0
        response['data'] = log_inst.type + log_inst.time + log_inst.msg + log_inst.location
        message = gene_django_frame(D_HEAD, D_VERSION, response)
        client_handler.send(message)
        return 1
    else:
        response['code'] = -1
        response['data'] = 'log list empty'
        message = gene_django_frame(D_HEAD, D_VERSION, response)
        client_handler.send(message)
        print 'log_inst is empty'
        return 1
        
def log_config(json_inst, client_handler):
    """
    控制设备
    
    :param json_inst: jeon 格式的对象
    :clent_handler: TCP连接句柄
    :rtype: 1 无误， 0 有误 
    """
    print 'in log config'
    response = {'uri' : 'config/log',
                'type': 'response',
                }
    if json_inst['data']['type'] == 'error':
        log_manager.log_configure(log_error = json_inst['data']['action'])
    elif json_inst['data']['type'] == 'communication':
        log_manager.log_configure(log_communication = json_inst['data']['action'])
    elif json_inst['data']['type'] == 'work':
        log_manager.log_configure(log_work= json_inst['data']['action'])
    elif json_inst['data']['type'] == 'debug':
        log_manager.log_configure(log_debug= json_inst['data']['action'])
    else:
        response['code'] = -1
        response['definition'] = 'unknow log type'
        message = gene_django_frame(D_HEAD, D_VERSION, response)
        client_handler.send(message)
        print 'unknow log type'
        return 0
    response['code'] = 0
    response['definition'] = 'config done'
    
    message = gene_django_frame(D_HEAD, D_VERSION, response)
    client_handler.send(message)
    return 1

django_protocal_buffer = {
    'device/controller/': device_controller,
    'device/viewer/'    : device_viewer,
    'config/log/'       : log_config, 
    'log/viewer'        : log_view,
     
                          }
