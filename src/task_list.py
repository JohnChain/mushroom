#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *

class Task():
    """
    任务类型
    """
    def __init__(self, birth_type = BIRTH_TYPE_AUTO, frame = '', birth_time = datetime.now()):
        #: 任务初始方向（UP/DOWN）
        self.birth_type = birth_type
        #: 来源套接字的文件描述符（用于到连接字典查询相应连接句柄）
        self.birth_fileno = -1
        #: 版本号
        self.version = -1
        #: 任务数据包
        self.frame = frame
        #: 生成时间
        self.birth_time = datetime.now()
        #:任务状态
        self.state = TASK_READY
        #:生成任务ID
        self.gene_id()
        
    def gene_id(self):
        GlobalTaskId.lock.acquire()
        #:任务ID
        self.id = GlobalTaskId.global_task_id
        GlobalTaskId.global_task_id += 1
        if GlobalTaskId.global_task_id > MAX_TASK_ID:
            GlobalTaskId.global_task_id = 0
        GlobalTaskId.lock.release()
        
class TaskList():
    #: 任务列表
    task_list = {}
    
    def add(self, one_task):
        """
        怎加任务
        
        :param one_task: 待插入的任务，类型为 Task 类
        :rtype: NULL
        """
        if task_condition.acquire():
            self.task_list[one_task.id] = one_task
            task_condition.notifyAll()
            task_condition.release()
            log_msg = 'One task added'
            log_handler.debug(log_msg)
    
    def remove(self, task_id):
        """
        删除任务
        
        :param task_id: 待删除的任务号
        :rtype: NULL
        """
        # ERROR************
        try:
            self.task_list.pop(task_id)
            
            log_msg = '[ Task Deliver ] Remove one task, id : %d' %(task_id)
            # log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)
            log_handler.work(log_msg)
            
        except KeyError:
            log_msg = 'In remove task key error'
            log_handler.error(log_msg)

class GlobalTaskId:
    global_task_id = 0
    lock = threading.Lock()

task_condition = threading.Condition(threading.Lock())
global_task_list = TaskList()

if __name__ == "__main__":
    task1 = Task()
    task2 = Task()
    task3 = Task()
    task1.task_id = 1
    task2.task_id = 2
    task3.task_id = 3
    global_task_list.add(task1)
    global_task_list.add(task2)
    global_task_list.add(task3)
    print len(global_task_list.task_list)
    for key in global_task_list.task_list.keys():
        print 'To remove task %d' %key
        global_task_list.remove(key)
    print len(global_task_list.task_list)
