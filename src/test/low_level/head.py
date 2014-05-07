#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import socket
from time import sleep
from datetime import datetime
from binascii import a2b_hex, b2a_hex

#============套接字队列模块配置=============#

ARM_SERVER_ADDR = ('127.0.0.1', 9000)
# ARM_SERVER_ADDR = ('192.168.1.166', 9000)
# ARM_SERVER_ADDR = ('10.18.50.66', 9000)

BIRTH_TYPE_MANUAL    = 0
BIRTH_TYPE_AUTO      = 1

#=============通信协议模块配置===============#
#----- 控制端——>数据层 -------#
#: 数据包头标志
A_HEAD = 'MUSHROOM'
#: 数据包结束符
A_END = a2b_hex('13')
#: 与Django通信信息包的版本号
A_VERSION = 1
#: 数据包长度占字节数
byte_pkg_len = 3
#: 数据包版本号
byte_version = 2
#: 业务层消息头占字节数
byte_m_header_len = 3

