#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *

class DjangoFrameSolution():
    """
    与Django通信数据包的解析与构造
    """

    def receive(self, handler):
        """
        接收数据包
                            
        :param handler: 连接句柄
        :rtype: 成功返回所收到的原数据包，失败返回 ''
        """
        frame = ''
        head = handler.recv(1)
        if head == D_HEAD[0] :
            head += handler.recv(2)
            if head == D_HEAD[:3]:
                head += handler.recv(len(D_HEAD)- 3)
                print head
                if head == D_HEAD:
                    version = handler.recv(1)
                    length = int(b2a_hex(handler.recv(4)), 16)
                    body = handler.recv(length)
                    
                    frame += head
                    frame += version
                    return version, body 
        return '', ''
        
    def send(self, handler, frame):
        """
        发送数据包
                            
        :param handler: 连接句柄
        :param frame: 待发数据包
        :rtype: 成功返回 发送字节数，否则返回 -1
        """
        handler.send(frame)
        return len(frame)

    def unpack(self, version, body):
        """
        拆包，判断帧头尾正确性，及完成校验任务
        
        :param origin_frame: 待解析的原始数据包
        :rtype: 成功，待反序列化的数据部分，否则返回空字符
        """
#         if origin_frame[:8] != D_HEAD:
#             print 'wrone head'
#             return ''
        return body
    
    def parse(self, json_frame):
        """
        构造器
        
        :param frame: 带构造成数据包的信息 
        :rtype: 成功返回 构造结果 ， 失败返回空字符串 
        """
        print json_frame
        return json.loads(json_frame)
        
    def dispatch(self, json_inst, client_handler):
        """
        解析器
        
        :param frame: 待解析的数据包
        :rtype: 【待定】
        """
        print json_inst