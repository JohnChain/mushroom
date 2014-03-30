#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from task_list import *

def generate_task(one_task, sub_frame, fileno, version, birth_type):
    """
    产生任务，加入到任务队列
    
    :param sub_frame: 完整的命令包格式 
    :param client_handler: 命令产生套接字文件描述符
    :rtype: 【待定】
    """
    one_task.birth_fileno = fileno
    one_task.version = version
    one_task.birth_type = birth_type
    one_task.frame = sub_frame
    global_task_list.add(one_task)

def gene_message_header(message_id, session, type, version, connection, source = BIRTH_TYPE_AUTO):
    temp_header = MessageHeader()
    temp_header.message_id  = message_id
    temp_header.session     = session
    temp_header.type        = type
    temp_header.connection  = connection
    temp_header.source      = source
    temp_header.version     = version
    
    # message_header          = temp_header.SerializeToString()
    return temp_header

def gene_arm_frame(message_header = '', data = '', ):
    if data != '':
        data = data.SerializeToString()
    if message_header != '':
        temp_message_header = message_header.SerializeToString()
        
    log_msg = 'message header: \n %s' %b2a_hex(temp_message_header)
    log_handler.debug(log_msg)
    
#     from head import *
    m_header_len = '{:{fill}{width}{base}}'.format(len(temp_message_header), fill = '0', width = 2 * A_header_byte, base = 'x')
    m_header_len = a2b_hex(m_header_len)
    
    log_msg = "heaer_len = %d" %len(temp_message_header)
#     log_handler.debug(log_msg)
    
    temp_pkg_len = len(temp_message_header) + len(data) + A_header_byte
    pkg_len = '{:{fill}{width}{base}}'.format(temp_pkg_len, fill = '0', width = 2 * A_pkg_byte, base = 'x')
    pkg_len = a2b_hex(pkg_len)
    
    log_msg = 'Pkg_len = %d' %temp_pkg_len
#     log_handler.debug(log_msg)
    
    main_frame = A_HEAD + pkg_len + m_header_len + temp_message_header + data
    return main_frame

def gene_django_frame(head, version, json_inst):
    Body = json.dumps(json_inst)
    Version = '{:{fill}{width}{base}}'.format(version, fill = '0', width = 2 * D_version_byte, base = 'x')
    Length  = '{:{fill}{width}{base}}'.format(len(Body), fill = '0', width = 2 * D_lenght_byte, base = 'x')
    message = head + a2b_hex(Version) + a2b_hex(Length) + Body
    return message