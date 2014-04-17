#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from utils import *

device_controller = {
    "uri" : "device/controller", 
    "type": "request",
    "data": {
              "roomId": 1,
              "controllerId": 1, 
              "action": 1,
              }
}

device_viewer = {
    "uri" : "device/viewer",
    "type": "request", 
    "data": {
            "roomId": 1, 
            "controllerId": 1,
            }
}

log_viewer = {
    "uri" : "log/viewer", 
    "type": "request", 
    "data": {
        "type": 'work',  #["error"/ "communication"/"debug"/"work"],
    }
}

sys_config_viewer = {
    "uri": "config/log", 
    "type": "request", 
    "data": {
             "type": "error", 
             "action": 1, 
             }
}

instance_updated = {
   "uri": "policy/now/update",
   "type": "request",
   }


def read_controller_state(room_id, controller_id):
    device_viewer['data']['roomId'] = room_id
    device_viewer['data']['controllerId'] = controller_id
    return gene_django_frame(D_HEAD, D_VERSION, device_viewer)
    
def update_controller_state(room_id, controller_id, state):
    device_controller['data']['roomId'] = room_id
    device_controller['data']['controllerId'] = controller_id
    device_controller['data']['action'] = state
    return gene_django_frame(D_HEAD, D_VERSION, device_controller)
    
def read_log_state(type):
    log_viewer['data']['type'] = type
    read_log_state_frame = gene_django_frame(D_HEAD, D_VERSION, log_viewer)
    return read_log_state_frame

def update_log_state(type, action):
    sys_config_viewer['data']['type'] = type
    sys_config_viewer['data']['action'] = action
    frame = gene_django_frame(D_HEAD, D_VERSION, sys_config_viewer)
    return frame

device_controller_frame = gene_django_frame(D_HEAD, D_VERSION, device_controller)
device_viewer_frame     = gene_django_frame(D_HEAD, D_VERSION, device_viewer)
log_viewer_frame        = gene_django_frame(D_HEAD, D_VERSION, log_viewer)
sys_config_viewer_frame = gene_django_frame(D_HEAD, D_VERSION, sys_config_viewer)

if __name__ == '__main__':
    print device_controller_frame
    print device_viewer_frame
    print log_viewer_frame
    print sys_config_viewer_frame