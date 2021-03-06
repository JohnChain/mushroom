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

        :rtype: 成功返回SUC， 失败返回 FAI，如果查过判断僵死时间，返回 ERR
        """
        result = FAI
        servant = DjangoFrameSolution()
        version, body = servant.receive(self.client.handler)
        if body != '':
            self.client.mylock.acquire()
            self.client.last_time = datetime.now()
            self.client.mylock.release()

            # 解析数据
            json_inst = servant.parse(body)
            # 带入计算公式计算
            result = servant.dispatch(json_inst, self.client.handler)
            
            log_msg = 'dispatch result = %d' %result
            log_handler.debug(log_msg)

            if result == SUC:
                return SUC
        now_time = datetime.now()
        gap = (now_time - self.client.last_time).seconds
        if gap > SOCKET_TIMEOUT:
            return ERR
        else:
            return FAI