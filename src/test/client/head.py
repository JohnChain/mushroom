#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import socket
from time import *
from datetime import *
from binascii import a2b_hex, b2a_hex

# 开
ON = 1
# 关
OFF = 0
# 成功
SUC = 0
# 失败
FAI = -1
# 异常
ERR = -2

#============套接字队列模块配置=============#
#: 对 ARM 提供链接服务的地址及端口
DJANGO_SERVER_ADDR = ('127.0.0.1', 9001)
#DJANGO_SERVER_ADDR = ('10.18.50.98', 9001)

#: 方向，本系统中包括 ARM 和 Django
BIRTH_TYPE_MANUAL    = 0
BIRTH_TYPE_AUTO      = 1

#=============通信协议模块配置===============#
#: 与Django通信消息包的头标志
D_HEAD = 'MUSHROOM'
#: 与Django通信信息包的版本号
D_VERSION = 1
#: 数据包版本号
D_version_byte = 1
#: 业务层消息头占字节数
D_lenght_byte = 4
