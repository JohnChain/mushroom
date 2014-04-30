#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from arm_frame_solution import ArmFrameSolution
from task_list import *

class ArmFrameMain():
    """
    此类负责处理每个连接实例，包括收发包，解析等操作
    """
    def __init__(self, client):
        self.client = client
        self.fileno = client.fileno()
    
    def main_receivor(self,):
        """
        连接实例主处理入口，收取数据， 解析数据， 处理数据
        
        :rtype: 成功返回SUC， 失败返回 FAI，如果查过判断僵死时间，返回 ERR
        """     
        servant = ArmFrameSolution()
        # 收数据
        origin_frame = servant.receive(self.client.handler)
        if len(origin_frame) > 0:
            
            log_msg = "Up main_receivor dealing message !"
            log_handler.debug(log_msg)

            log_msg = 'From ARM ONE FULL FRAME: \n%s' %b2a_hex(origin_frame)
            log_handler.communication(log_msg)
            
            self.client.mylock.acquire()
            self.client.last_time = datetime.now()
            self.client.mylock.release()
            
            # 解包
            protobuf_msg_dic = servant.unpack(origin_frame)
            if protobuf_msg_dic == '':
                return FAI
            # 反序列化
            protobuf_inst = servant.parse(protobuf_msg_dic)
            if protobuf_inst == '':
                return FAI
            # 分发数据
            result = servant.dispatch(protobuf_inst, self.client.fileno())
            return result
        else:
            now_time = datetime.now()
            gap = (now_time - self.client.last_time).seconds
            if gap > SOCKET_TIMEOUT:
                return ERR
            else:
                return FAI
