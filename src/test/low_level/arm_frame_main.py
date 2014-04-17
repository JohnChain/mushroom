#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from arm_frame_solution import ArmFrameSolution


class ArmFrameMain():
    """
    此类负责处理每个连接实例，包括收发包，解析等操作
    """
    def __init__(self, handler):
        self.handler = handler
    
    def main_receivor(self,):
        """
        连接实例主处理入口，收取数据， 解析数据， 处理数据
        
        :rtype: 如果接受数据不为空， 返回 1， 如果查过判断僵死时间，返回 -1， 否则返回 0
        """
        servant = ArmFrameSolution()
        # 收数据
        origin_frame = servant.receive(self.handler)
        if len(origin_frame) > 0:
            print "UP MAIN THREAD STARTED !"
            
            # 解包
            protobuf_msg_dic = servant.unpack(origin_frame)
            if protobuf_msg_dic == '':
                return -1
            # 反序列化
            protobuf_inst = servant.parse(protobuf_msg_dic)
            if protobuf_inst == '':
                return -1
            # 分发数据
            result = servant.dispatch(protobuf_inst, self.handler)
            return 1
        else:
            pass
#             print 'get on empyt pack'