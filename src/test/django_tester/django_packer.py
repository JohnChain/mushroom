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


device_controller_frame = gene_django_frame(D_HEAD, D_VERSION, device_controller)
device_viewer_frame     = gene_django_frame(D_HEAD, D_VERSION, device_viewer)
log_viewer_frame        = gene_django_frame(D_HEAD, D_VERSION, log_viewer)
sys_config_viewer_frame = gene_django_frame(D_HEAD, D_VERSION, sys_config_viewer)

if __name__ == '__main__':
    print device_controller_frame
    print device_viewer_frame
    print log_viewer_frame
    print sys_config_viewer_frame