#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from task_list import *
from mushroom_pb2 import *
from utils import *

def device_update(json_inst, client_handler):
    """
    发送控制命令的数据包
    
    :param json_inst: jeon 格式的对象
    :clent_handler: TCP连接句柄
    :rtype: SUC 无误， FAI 有误 
    """
    log_msg = 'In device_update...'
    log_handler.debug(log_msg)
    
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
    
    log_msg = 'To ARM UPDATE_CONTROLLER_STATE -- %s' %b2a_hex(main_frame)
    log_handler.communication(log_msg)

    generate_task(one_task, main_frame, client_handler.fileno(), version, BIRTH_TYPE_MANUAL)
    return SUC
    
def device_view(json_inst, client_handler):
    """
    查看设备的运行状态
    
    :param json_inst: jeon 格式的对象
    :clent_handler: TCP连接句柄
    :rtype: SUC 无误， FAI 有误 
    """
    log_msg = 'In device_view...'
    log_handler.debug(log_msg)

    one_task = Task()
    version = A_VERSION
    type    = 1
    message_header = gene_message_header(READ_CONTROLLER_STATE, one_task.id, type, version, client_handler.fileno(), BIRTH_TYPE_MANUAL)
    
    data = Controller()
    data.controller_id = int(json_inst['data']['controllerId'])
#     data.room.room_id = json_inst['data']['roomId']
    
    main_frame = gene_arm_frame(data = data, message_header = message_header)
    
    log_msg = 'To ARM READ_CONTROLLER_STATE -- %s' %b2a_hex(main_frame)
    log_handler.communication(log_msg)

    generate_task(one_task, main_frame, client_handler.fileno(), version, BIRTH_TYPE_MANUAL)
    return SUC

# def log_view(json_inst, client_handler):
#     """
#     控制设备
#     
#     :param json_inst: jeon 格式的对象
#     :clent_handler: TCP连接句柄
#     :rtype: SUC 无误， FAI 有误, ERR 异常
#     """
#     log_msg = 'In log view'
#     log_handler.debug(log_msg)
# 
#     # log_inst = log_manager.view_record(json_inst['type'])
#     
#     response = {'uri': 'log',
#                 'type': 'response',
#                 }
#     if log_inst != '': 
#         response['code'] = 0
#         response['data'] = log_inst.type + log_inst.time + log_inst.msg + log_inst.location
#         message = gene_django_frame(D_HEAD, D_VERSION, response)
# 
#         client_handler.send(message)
#     else:
#         response['code'] = -1
#         response['data'] = 'log list empty'
#         message = gene_django_frame(D_HEAD, D_VERSION, response)
#         client_handler.send(message)
#         log_msg = 'log list is empty'
#         log_handler.debug(log_msg)
#     
#     log_msg = 'To django log_view response -- head: %s, version: %d, json: %s' %(D_HEAD, D_VERSION, json.dumps(response))
#     log_handler.communication(log_msg)
#     return SUC

def log_config(json_inst, client_handler):
    """
    控制设备
    
    :param json_inst: jeon 格式的对象
    :clent_handler: TCP连接句柄
    :rtype: SUC 无误， FAI 有误 
    """
    log_msg = 'In log config'
    log_handler.debug(log_msg)

    response = {'uri' : 'config/log',
                'type': 'response',
                }
    if json_inst['data']['type'] == 'error':
        # log_manager.log_configure(log_error = json_inst['data']['action'])
        if json_inst['data']['action'] == ON:
            log_handler.enable_error()
        else:
            log_handler.disable_error()
    elif json_inst['data']['type'] == 'communication':
        # log_manager.log_configure(log_communication = json_inst['data']['action'])
        if json_inst['data']['action'] == ON:
            log_handler.enable_communication()
        else:
            log_handler.disable_communication()
    elif json_inst['data']['type'] == 'work':
        # log_manager.log_configure(log_work= json_inst['data']['action'])
        if json_inst['data']['action'] == ON:
            log_handler.enable_work()
        else:
            log_handler.disable_work()
    elif json_inst['data']['type'] == 'debug':
        # log_manager.log_configure(log_debug= json_inst['data']['action'])
        if json_inst['data']['action'] == ON:
            log_handler.enable_debug()
        else:
            log_handler.disable_debug()
    else:
        response['code'] = -1
        response['definition'] = 'unknow log type'
        message = gene_django_frame(D_HEAD, D_VERSION, response)
        client_handler.send(message)
        log_msg = 'unknow log type'
        log_handler.debug(log_msg)

        log_msg = 'To django log_config response -- head: %s, version: %d, json: %s' %(D_HEAD, D_VERSION, json.dumps(response))
        log_handler.communication(log_msg)
        return FAI
    response['code'] = 0
    response['definition'] = 'config done'
    
    message = gene_django_frame(D_HEAD, D_VERSION, response)
    client_handler.send(message)

    log_msg = 'To django log_config response -- head: %s, version: %d, json: %s' %(D_HEAD, D_VERSION, json.dumps(response))
    log_handler.communication(log_msg)
    return SUC

django_protocal_buffer = {
    'device/controller/': device_update,
    'device/viewer/'    : device_view,
    'config/log/'       : log_config, 
#     'log/viewer'        : log_view,
     
                          }
