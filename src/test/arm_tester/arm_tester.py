#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from arm_packer import *
from arm_frame_main import *
"""
此文件用于测试 socket_list.py 文件
"""
def main():
    print "Connect to the server"
    arm_tester = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    arm_tester.connect(ARM_SERVER_ADDR)
    print 'connection done...'

    receiver = ArmFrameMain(arm_tester)
    while 1:
        receiver.main_receivor()

if __name__ == '__main__':
    main()