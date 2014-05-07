#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
import ConfigParser

def read_config():
    try:
        config_inst = ConfigParser.ConfigParser()
        config_inst.read('mushroom.conf')

        ####################################################
        db_conn_info['HOST']        = config_inst.get('DB', 'host')
        db_conn_info['USER']        = config_inst.get('DB', 'user')
        db_conn_info['PASSWORD']    = config_inst.get('DB', 'password')
        db_conn_info['DATABASE']    = config_inst.get('DB', 'database')

        ####################################################
        arm_server_addr = config_inst.get('ARMServer', 'address')
        arm_server_port = config_inst.getint('ARMServer', 'port')
        ARM_SERVER_ADDR[0] = arm_server_addr
        ARM_SERVER_ADDR[1] = arm_server_port

        django_server_addr = config_inst.get('DjangoServer', 'address')
        django_server_port = config_inst.getint('DjangoServer', 'port')
        DJANGO_SERVER_ADDR[0] = django_server_addr
        DJANGO_SERVER_ADDR[1] = django_server_port

        ####################################################
        log_file['ERROR']           = config_inst.get('Log', 'error_path')
        log_file['COMMUNICATION']   = config_inst.get('Log', 'communication_path')
        log_file['DEBUG']           = config_inst.get('Log', 'debug_path')
        log_file['WORK']            = config_inst.get('Log', 'work_path')

        if config_inst.getint('Log', 'error_open') == 1:
            log_handler.enable_error()
        else:
            log_handler.disable_error()
        if config_inst.getint('Log', 'communication_open') == 1:
            log_handler.enable_communication()
        else:
            log_handler.disable_communication()
        if config_inst.getint('Log', 'debug_open') == 1:
            log_handler.enable_debug()
        else:
            log_handler.disable_debug()
        if config_inst.getint('Log', 'work_open') == 1:
            log_handler.enable_work()
        else:
            log_handler.disable_work()

        ####################################################
        MAX_TASK_ID = config_inst.getint('Task', 'max_session_id')
        if MAX_TASK_ID > 16777215:
            MAX_TASK_ID = 16777215

        ####################################################

        return SUC
    except ConfigParser.Error, e:
        log_msg = str(e)
        log_handler.error(log_msg)
        return FAI

if __name__ == '__main__':
    read_config()

    print db_conn_info
    print 'ARM_SERVER_ADDR: %s' %str(ARM_SERVER_ADDR)
    print 'DJANGO_SERVER_ADDR: %s' %str(DJANGO_SERVER_ADDR)
    print 'log_file: %s' %str(log_file)
    print 'log_conf: %s' %str(log_conf)
    print 'MAX_TASK_ID: %d' %MAX_TASK_ID
