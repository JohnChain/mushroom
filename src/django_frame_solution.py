#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from django_protocal import *

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
                
                log_msg = 'From django received full head : %s' %head
                log_handler.debug(log_msg)

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

    def parse(self, json_frame):
        """
        构造器
        
        :param frame: 带构造成数据包的信息 
        :rtype: 成功返回 构造结果 ， 失败返回空字符串 
        """
        log_msg = 'From django -- %s' %json_frame
        log_handler.communication(log_msg)
        
        return json.loads(json_frame)
        

    def dispatch(self, json_inst, client_handler):
        """
        解析器
        
        :param frame: 待解析的数据包
        :rtype: 【待定】
        """
        if json_inst['uri'] == "device/controller":
            if json_inst['type'] == 'request':
                return device_update(json_inst, client_handler)
        elif json_inst['uri'] == 'device/viewer':
            if json_inst['type'] == 'request':
                return device_view(json_inst, client_handler)
        elif json_inst['uri'] == 'config/log':
            if json_inst['type'] == 'request':
                return log_config(json_inst, client_handler)
        elif json_inst['uri'] == "device/controller/sync":
            pass
        elif json_inst['uri'] == "policy/now/update":
            if json_inst['type'] == 'request':
                return policy_instance_updated(json_inst, client_handler)
        elif json_inst['uri'] == "log/viewer":
            if json_inst['type'] == 'request':
                return log_view(json_inst, client_handler)
        else:
            log_msg = 'Unknow uri'
            log_handler.communication(log_msg)

            return 0