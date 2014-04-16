#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import json
import Queue
import ctypes
import select
import socket
import logging
import threading
from time import sleep
from datetime import datetime, timedelta
from threading import Event, Timer
from signal import signal, SIGINT
from binascii import a2b_hex, b2a_hex

try:
    from mushroom_pb2 import *
    sensor_type_dict = {
           TEMP : 'temperature',
           LIGHT: 'light',
           HUMI : 'humidity',
           CO2  : 'co2',
        }
    
    controller_type_dict = {
           XUNHUAN_FAN  : 'xunhuan_fan',
           JINFENG_FAN  : 'jinfeng_fan',
           PAIFENG_FAN  : 'paifeng_fan',
           JIASHIQI     : 'jiashiqi',
           YASUOJI      : 'yasuoji',
           NEIJI        : 'neiji',
           YELLOW_LIGHT : 'yello_light',
           RED_LIGHT    : 'red_light',
           BLUE_LIGHT   : 'blue_light',
       }
except Exception:
    pass

sys_config_dict = {
        'TIME_SYNC_CYCLE' : 50,
    }

room_dict = {
        'sensor': [],
        'controller': [],
    }

# 开
ON  = 1
# 关
OFF = 0
# 成功
SUC = 0
# 失败
FAI = -1
# 异常
ERR = -2

# 全局线程队列    
thread_dict = {}
THREAD_TASK     = 'task_deliver'
THREAD_ARM      = 'arm_server' 
THREAD_DJANGO   = 'django_server'
THREAD_POLICY   = 'threshold_loader'


#===========执行策略相关=================#
# 环境限定范围，由单独的线程负责不断刷新，键为房间号，值为一个队列，长度始终为2.
# 其中第一个值为包含了当前使用的环境限定范围的元组，第二个值下一次刷新时间
threshold = {}
#:环境限制条件载入周期
THRESHOLD_LOAD_CYCLE = 10

#============任务队列模块配置==============#
#: 任务超时时长（s）
TASK_TIMEOUT        = 5
#:最大任务号
MAX_TASK_ID         = 99999
# 任务线程条件变量等待周期
TASK_WAIT_CIRCLE    = 1
#:任务就绪状态

TASK_READY          = 0
#:任务等待状态
TASK_WAITING        = 1
#:任务完成状态
TASK_FINISHED       = 2

#============套接字队列模块配置=============#
#: select 超时时间
SELECT_TIMEOUT      = 2
#: 僵尸套接字连接判断时间
SOCKET_TIMEOUT      = 10
#: 对 ARM 提供链接服务的地址及端口
ARM_SERVER_ADDR     = ('10.18.50.66', 9000)
#: 对 Django 提供链接服务的地址及端口 
DJANGO_SERVER_ADDR  = ('10.18.50.66', 9001)

#: 方向，本系统中包括 ARM 和 Django
BIRTH_TYPE_MANUAL   = 0
BIRTH_TYPE_AUTO     = 1

arm_client_list     = []
arm_client_dic      = {}
django_client_list  = []
django_client_dic   = {}

#==============数据库模块配置=============#
try:
    import pyodbc
except Exception:
    print "pyodbc not installed, please install it first"
    sys.exit()
    
#: 数据库连接参数
db_conn_info = {
    "HOST"      : "10.18.50.66",
#     "HOST"      : "127.0.0.1",
    "USER"      : "wsngump",
    "PASSWORD"  : "wsngump",
    "DATABASE"  : "mushroom",
}

POLICY_NEW      = 2
POLICY_RUNNING  = 1
POLICY_OLD      = 0

#=============日志模块配置===============#
#: 日志配置参数
log_conf = {
    'ERROR'         : ON,
    'COMMUNICATION' : ON,
    'DEBUG'         : ON,
    'WORK'          : ON,
}

log_file = {
    'ERROR'         : '..\log\error.txt',
    'COMMUNICATION' : '..\log\communication.txt',
    'WORK'          : '..\log\work.txt',
    'DEBUG'         : '..\log\debug.txt',
}

LOG_TIMER_CYCLE = 1

#: 全局日志管理器
try:
    from log_manager import Logger
    # log_manager = LogManager()
    log_handler = Logger('', )
except Exception:
    pass

#=============通信协议模块配置===============#
#----- 控制端——>数据层 -------#
#: 数据包头标志
A_HEAD = 'MUSHROOM'
#: 数据包结束符
A_END = a2b_hex('13')
#: 与Django通信信息包的版本号
A_VERSION = 1
#: 数据包长度占字节数
A_pkg_byte = 3
#: 数据包版本号
# A_version_byte = 2
#: 业务层消息头占字节数
A_header_byte = 3
#收数据超时
RECV_TIMEOUT = 3

#: 与Django通信消息包的头标志
D_HEAD = 'MUSHROOM'
#: 与Django通信信息包的版本号
D_VERSION = 1
#: 数据包版本号
D_version_byte = 1
#: 业务层消息头占字节数
D_lenght_byte = 4
