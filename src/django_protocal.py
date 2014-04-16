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
    if json_inst['data']['action'] == 'on'or json_inst['data']['action'] == 'ON':
        data.state = Controller.OPEN
    else:
        data.state = Controller.CLOSE
#     data.room.room_id = json_inst['data']['roomId']
    version = 1
    
    main_frame = gene_arm_frame(message_header = message_header, data = data, )
    
    log_msg = 'To ARM UPDATE_CONTROLLER_STATE -- \n%s' %(b2a_hex(main_frame))
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
#     print log_conf
#      
#     response = {'uri': 'log',
#                 'type': 'response',
#                 'code': SUC,
#                 'data': {},
#                 }
#     if log_conf['WORK'] == ON:
#         response['data']['work'] = 'on'
#     else:    
#         response['data']['work'] = 'off'
#         
#     if log_conf['ERROR'] == ON:
#         response['data']['error'] = 'on'
#     else:    
#         response['data']['error'] = 'off'
#         
#     if log_conf['COMMUNICATION'] == ON:
#         response['data']['communication'] = 'on'
#     else:    
#         response['data']['communication'] = 'off'
#         
#     if log_conf['DEBUG'] == ON:
#         response['data']['debug'] = 'on'
#     else:    
#         response['data']['debug'] = 'off'
#         
#     message = gene_django_frame(D_HEAD, D_VERSION, response)
#     client_handler.send(message)
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
        if json_inst['data']['action'] == ON:
            log_handler.enable_error()
        else:
            log_handler.disable_error()
    elif json_inst['data']['type'] == 'communication':
        if json_inst['data']['action'] == ON:
            log_handler.enable_communication()
        else:
            log_handler.disable_communication()
    elif json_inst['data']['type'] == 'work':
        if json_inst['data']['action'] == ON:
            log_handler.enable_work()
        else:
            log_handler.disable_work()
    elif json_inst['data']['type'] == 'debug':
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
    
    print log_conf
    return SUC

def policy_instance_updated(json_inst, client_handler):
    # 重启load_threshold线程
    from my_thread import MyThread
    from load_threshold import load_threshold
    thread_dict[THREAD_POLICY].join()
    threshold_loader = MyThread(THREAD_POLICY, load_threshold, ('', ))
    threshold_loader.start()
    thread_dict[THREAD_POLICY] = threshold_loader
    # 解决线程重启后内存中记录的下一次策略的时间，需要变动问题
    now_time = datetime.now()
    for room in threshold.keys():
        threshold[room][1] = (room, now_time) 
    return SUC
    
django_protocal_buffer = {
    'device/controller/': device_update,
    'device/viewer/'    : device_view,
    'config/log/'       : log_config, 
}
