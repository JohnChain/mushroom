#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from mushroom_pb2 import *
from arm_protocal import arm_protocal

class ArmFrameSolution():
    """
    与RAM通信数据包的解析与构造
    """
    def __init__(self):
        pass

    def receive(self, handler):
        """
        接收数据包
        
        :param handler: 连接句柄
        :rtype: 成功返回所收到的原数据包，失败返回 ''
        """
        frame = ''
        cup = handler.recv(1)
        if cup == A_HEAD[0]:
            frame += cup
            cup = handler.recv(1)
            if cup == A_HEAD[1]:
                frame += cup
                cup = handler.recv(len(A_HEAD) - 2)
                if cup == A_HEAD[2:]:
                #TODO: 检测空字符和超长数据 
                    frame += cup
                    cup = handler.recv(A_pkg_byte)
                    frame += cup
                    pkg_len = int(b2a_hex(cup), 16)
                    frame += handler.recv(pkg_len)
                    #TODO: 读取超时处理
                    return frame
        return ''
        
    def send(self, handler, frame):
        """
        发送数据包
                            
        :param handler: 连接句柄
        :param frame: 待发数据包
        :rtype: 成功返回 发送字节数，否则返回 -1
        """
        handler.send(frame)
        return len(frame)
    
    def generator(self, frame):
        """
        构造器
        
        :param frame: 带构造成数据包的信息 
        :rtype: 成功返回 构造结果 ， 失败返回空字符串 
        """
        return frame

    def unpack(self, frame):
        """
        拆包，判断帧头尾正确性，及完成校验任务
        
        :param frame: 待解析的数据包
        :rtype: 成功返回拆包后的字典，否则返回空字符
        """
#         len_head = len(HEAD)
#         if frame[:len_head] != HEAD:
#             print 'wrone head'
#             return ''
        frame = frame[len(A_HEAD):]
        pkg_len = int(b2a_hex(frame[:A_pkg_byte]), 16)
        frame = frame[A_pkg_byte:]
        
#         version = int(b2a_hex(frame[:byte_version]), 16)
#         frame = frame[byte_version:]
        
        header_len = int(b2a_hex(frame[:A_header_byte]), 16)
        frame = frame[A_header_byte:]
        
        message_header = frame[:header_len]
        data = frame[header_len:]
        
        temp_dict = {
                'message_header' : message_header,
                'data'           : data,
                }
        log_msg = 'Receive From ARM: pkg_len = %d    header_len = %d    header = %s    data = %s ' %(pkg_len, header_len, message_header, data) 
        log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)
        return temp_dict
    
    def parse(self, protobuf_msg_dic):
        data_inst = ''
        
        header_inst = MessageHeader()
        header_inst.ParseFromString(protobuf_msg_dic['message_header'])
        
        proto_inst = {'header_inst':header_inst, 'data':protobuf_msg_dic['data']}

        return proto_inst
    
    
    body_dict = {
                 1: arm_protocal ,
                 }
    
    def dispatch(self, proto_inst, birth_fileno):
        """
        解析器
        
        :param frame: 待解析的数据包
        :rtype: 【待定】
        """
        message_id = proto_inst['header_inst'].message_id
        version = proto_inst['header_inst'].version
        return self.body_dict[version][message_id](proto_inst, birth_fileno)
