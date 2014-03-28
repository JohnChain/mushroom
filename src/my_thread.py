#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from task_list import Task, TaskList

class MyThread(threading.Thread):
    """
    自定义线程类
    """

    def __init__(self, name, func, param):
        threading.Thread.__init__(self,)
        #: 线程名称
        self.name = name
        #: 线程所要执行的函数
        self.func = func
        #: 线程执行函数参数
        self.param = param

        self.stop_Event = Event()

    def run(self):
        """
        继承并重载父类run函数，线程启动时首先执行的函数

        :rtype: 尚无返回
        """

        self.func(self.stop_Event, self.param, )

    def join(self):
        self.stop_Event.set()
        try:
            threading.Thread.join(self)
        except threading.thread.error, e:
            log_msg = str(e)
            log_handler.error(e)


