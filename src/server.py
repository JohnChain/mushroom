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

main_event = Event()

def handler(signal, frame):
    log_msg = '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n'
    log_msg += 'Main process is going to shutdown : '
    log_handler.work(log_msg)

    main_event.set()
    for thread_name in thread_dict.keys():
        thread_dict[thread_name].join()

    log_msg = 'System Shutdown'
    log_handler.work(log_msg)

    sys.exit()

def main():
    """
    主函数

    :rtype: 0
    """
    log_msg = 'Start From Main Function'
    log_handler.work(log_msg)

    print read_config()
    print 'db_conn_info:%s' %str(db_conn_info)
    print 'arm_server: %s' %str(ARM_SERVER_ADDR)
    print 'django_server: %s' %str(DJANGO_SERVER_ADDR)
    print 'Log_files: %s' %str(log_file)
    print 'log_conf: %s' %str(log_conf)

    temp_task = TaskDeliver()
    task_deliver = MyThread(THREAD_TASK, temp_task.core, ('', ))
    task_deliver.start()

    threshold_loader = MyThread(THREAD_POLICY, load_threshold, ('', ))
    threshold_loader.start()

    temp_ram = SocketList(ArmFrameMain, arm_client_list)
    temp_ram.init(tuple(ARM_SERVER_ADDR), 10)
    ram_server = MyThread(THREAD_ARM, temp_ram.manage_list, ('', ))
    ram_server.start()

    temp_django = SocketList(DjangoFrameMain, django_client_list)
    temp_django.init(tuple(DJANGO_SERVER_ADDR), 10)
    django_server = MyThread(THREAD_DJANGO, temp_django.manage_list, ('', ))
    django_server.start()

    global thread_dict
    thread_dict[THREAD_TASK]    = task_deliver
    thread_dict[THREAD_ARM]     = ram_server
    thread_dict[THREAD_DJANGO]  = django_server
    thread_dict[THREAD_POLICY]  = threshold_loader

    signal(SIGINT, handler)
    try:
        while not main_event.isSet():
            sleep(0.01)
    except KeyboardInterrupt:
        for thread_name in thread_dict.keys():
            thread_dict[thread_name].join()
        sys.exit()

if __name__ == "__main__":
    main()
