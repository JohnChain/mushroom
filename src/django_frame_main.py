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
        #log_msg = 'In DjangoFrameMain, later will server one client'
        #log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)

        servant = DjangoFrameSolution()
        version, body = servant.receive(self.client.handler)
        if body != '':
            print "DOWN MAIN THREAD STARTED !"
            self.client.mylock.acquire()
            self.client.last_time = datetime.now()
            self.client.mylock.release()

            # 拆包得到json数据部分
            json_frame = servant.unpack(version, body)
            # 解析数据
            json_inst = servant.parse(json_frame)
            # 带入计算公式计算
            result = servant.dispatch(json_inst, self.client.handler)
            print 'dispatch result = %d' %result
            if result == 1:
                return result
        now_time = datetime.now()
        gap = (now_time - self.client.last_time).seconds
        if gap > SOCKET_TIMEOUT:
            return -1
        else:
            return 0
