#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from django_packer import *
from django_frame_main import *
"""
此文件用于测试 socket_list.py 文件
"""
def main():
    print "Connect to the server"
    django_tester = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    django_tester.connect(DJANGO_SERVER_ADDR)
    dj_reciver = DjangoFrameMain(django_tester)
    print 'connection done...'
#     django_tester.send(sys_config_viewer_frame)
#     print django_tester.recv(1024)
#     django_tester.send(device_controller_frame)
#     dj_reciver.main_receivor()
# 
#     django_tester.send(device_viewer_frame)
#     dj_reciver.main_receivor()
    
    django_tester.send(instance_updated_frame)

    django_tester.close()
if __name__ == '__main__':
    main()
