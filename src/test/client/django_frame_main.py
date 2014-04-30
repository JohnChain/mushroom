#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from django_frame_solution import DjangoFrameSolution

class DjangoFrameMain():
    """
    此类负责处理每个连接实例，包括收发包，解析等操作
    """
    def __init__(self, client):
        self.client = client
        self.fileno = client.fileno()
        
    def main_receivor(self, ):
        """
        连接实例主处理入口，收取数据
        
        :rtype: 如果接受数据不为空， 返回 1， 如果查过判断僵死时间，返回 -1， 否则返回 0
        """
        servant = DjangoFrameSolution()
        version, body = servant.receive(self.client)
        if body != '':

            # 解析数据 
            json_inst = servant.parse(body)
            return json_inst
        