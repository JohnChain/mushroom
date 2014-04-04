#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from socket_list import SocketList
from my_thread import MyThread
from arm_frame_main import ArmFrameMain
from django_frame_main import DjangoFrameMain
from task_deliver import TaskDeliver
from load_threshold import load_threshold
from env_init import read_config

def handler(signal, frame):
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    log_msg = 'Main process is going to shutdown : '
    log_handler.work(log_msg)
#     log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)
#     print log_msg
    
    main_event.set()
    for thread in thread_list:
        thread.join()
        
    log_msg = 'System Shutdown'
    log_handler.work(log_msg)
    
    sys.exit()
    
main_event = Event()
thread_list = []

def main():
    """
    主函数
    
    :rtype: 0
    """
    log_msg = 'Start From Main Function'
    log_handler.work(log_msg)
    
    read_config()
    
    temp_task = TaskDeliver()
    task_deliver = MyThread('task_deliver', temp_task.core, ('', ))
    task_deliver.start()
    
    threshold_loader = MyThread('load threshold', load_threshold, ('', ))
    threshold_loader.start()
    
    temp_ram = SocketList(ArmFrameMain, arm_client_list)
    temp_ram.init(ARM_SERVER_ADDR, 10)
    ram_server = MyThread('ram_server', temp_ram.manage_list, ('', ))
    ram_server.start()
    
    temp_django = SocketList(DjangoFrameMain, django_client_list)
    temp_django.init(DJANGO_SERVER_ADDR, 10)
    django_server = MyThread('django_server', temp_django.manage_list, ('', ))
    django_server.start()
    
    global thread_list
    thread_list.append(task_deliver)
    thread_list.append(ram_server)
    thread_list.append(django_server)
    thread_list.append(threshold_loader)
    
    signal(SIGINT, handler)
    try:
        while not main_event.isSet():
            sleep(0.01)
    except KeyboardInterrupt:
        for thread in thread_list:
            thread.join()
        sys.exit()
    
if __name__ == "__main__":
    main()
