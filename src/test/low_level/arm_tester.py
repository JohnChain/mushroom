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
    arm_tester.send(init())
    arm_tester.send(read_time())
#     receiver.main_receivor()
#     arm_tester.send(push_sensor_data())
    while 1:
        receiver.main_receivor()
        

if __name__ == '__main__':
    main()
