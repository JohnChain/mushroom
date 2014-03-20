#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 该自定键值映射参照数据库设计文档
light_color = {
       1 : 'white',
       2 : 'blue',
       3 : 'yellow', 
       }

class PolicyInstance:    
    """
    策略实例类型
    """
    #: 实例号
    instance_id = -1
    #: 策略号 
    policy_id   = -1
    #: 植被号
    plant_id    = -1
    #: 房间号
    room_id     = -1
    #: 实例执行开始时间
    start_time  = -1
    
class AbsoluteTime:
    """
    绝对时间类型
    对应数据库中的 tb_absolute_time 表
    """
    #: 步骤号
    rule_id = -1
    #: 实例号
    instance_id = -1
    #: 更改时间
    change_time = ''

class TableSensor:
    sensor_id = -1
    sensor_name = ''
    room_id = -1
    position = []
    state = 1

class TablePlant:
    plant_id = -1
    plant_name = ''
    
class TableRoom:
    room_id = -1
    room_description = ''
