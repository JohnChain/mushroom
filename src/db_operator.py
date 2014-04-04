#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from db_base import MssqlConnection
from db_env import *

class DbOperator(MssqlConnection):
    def __init__(self, serverIp = db_conn_info['HOST'], dbName = db_conn_info['DATABASE'], \
                 uid = db_conn_info['USER'], pwd = db_conn_info['PASSWORD']):
        MssqlConnection.__init__(self, serverIp, dbName, uid, pwd)
    
    def get_latest_data(self, room_id):
        """
        通过房间ID查询实时的数据
        
        :param room_id: 传感器ID
        :rtype: json格式化字典
        """
        sql_str = "select top 1 instance_id, sense_time, room_id from tb_instance where room_id = %d order by instance_id desc " %(room_id)
        self.connect()
        result = self.queryAll(sql_str)
        
        instance_id = result[0][0]
        sense_time  = result[0][1].strftime('%Y/%m/%d %H:%M:%S')
        
        sql_str = '''select tb_data.sensor_id, data, sensor_type from tb_data left join tb_sensor
                        on tb_sensor.sensor_id = tb_data.sensor_id
                    where instance_id = %d''' %instance_id
        result = self.queryAll(sql_str)
        self.close()
        
        json_inst = {'instance_id'  : instance_id,
                     'sense_time'   : sense_time,
                     'room_id'      : room_id,
                     'sense_data'   :{
                                      'temperature' : [],
                                      'humidity'    : [],
                                      'co2'         : [],
                                      'light'       : [],
                                      }
                    }
        
        for one_row in result:
            sensor_type = one_row[2]
            sensor_id   = one_row[0]
            data        = one_row[1]
            
            json_inst['sense_data'][sensor_type].append({'id': sensor_id, 'data': data})
        
        return json_inst
 
    def get_room_info(self, room_id):
        """
        通过Room ID获取房间信息
        
        :param room_id: 房间号
        :rtype: 待定
        """
        plant_dict = {}
        self.connect()
        sql_str = u'''select top 1 tb_room.room_id, room_description, tb_plant.plant_id, plant_name, policy_id from 
                            tb_policy_instance left join tb_plant 
                            on tb_policy_instance.plant_id = tb_plant.plant_id, tb_room
                      where tb_policy_instance.policy_instance_id in (select distinct policy_instance_id from tb_absolute_time) 
                            and tb_room.room_id = %d and state >= %d''' %(room_id, POLICY_RUNNING)
        # 这里有一个问题，当用户向tb_policy_instance表中一次添加了多个（>=2）个同房间不同开始时间的policy_instance时，
        # 理论上是可以的，但这时就会有上述的查询返回多组，其中只有一组是正在执行的，其他的均为当前执行周期结束后才执行的新的周期。
        plant_room = self.queryAll(sql_str)
        self.close()
        try:
            plant_dict['roomId']    = plant_room[0][0]
            plant_dict['roomName']  = plant_room[0][1]
            plant_dict['plantId']   = plant_room[0][2]
            plant_dict['plantName'] = plant_room[0][3]
            plant_dict['nowPolicy'] = plant_room[0][4]
        except IndexError, e:
            print 'get nothing in room_id: %d' %room_id
        return plant_dict
    
    def get_all_room(self):
        """
        获取所有房间的最新基础信息
        
        :rtype: 所有房间信息的队列
        """
        sql_str = '''
                select room_id from tb_room
                '''
        self.connect() 
        room_list = self.queryAll(sql_str)
        self.close()
        all_room_info = []
        for i in room_list:
            all_room_info.append(self.get_room_info(i[0]))
            
        return all_room_info
    
    def get_time_reange_data(self, room_id, start_time, end_time):
        """
        获取指定房间的指定范围环境信息（采集值）
        
        :param room_id: 房间号
        :param start_time: 开始时间
        :param end_time: 结束时间
        :rtype: 指定时间段的数据队列
        """
        sql_str = u'''
                    select tb_temp.sensor_id, tb_sensor.sensor_type, position, sense_time, data from 
                    (select sensor_id, sense_time, data 
                        from tb_data left join tb_instance on tb_instance.instance_id = tb_data.instance_id
                            where sense_time >= '%s' and sense_time < '%s' and room_id = %d) as tb_temp
                    left join tb_sensor on tb_temp.sensor_id = tb_sensor.sensor_id
                    order by sensor_id, sense_time
  
                    ''' %(start_time, end_time, room_id)
        self.connect()
        data = self.queryAll(sql_str)
        self.close()
        temp = {}
        temp['sensorId'] = data[0][0]
        temp['sensorName'] = data[0][1]
        temp['position'] = data[0][2]
        
        data_list = []
        for i in data:
            data_list.append((i[3].strftime('%Y/%m/%d %H:%M:%S'), i[4]))
        temp['values'] = tuple(data_list)

        return temp

    def certain_sensor_time_range_data(self, sensor_id, start_time, end_time):
        """
        通过sensor_id查询一段时间的数据
        
        :param sensor_id: 传感器ID
        :param start_time: 起时间
        :param end_time: 末时间
        :rtype: json格式化字典
        """
        sql_str = '''
                    select sense_time, position, sensor_type, data from 
                        tb_data left join tb_instance on tb_data.instance_id = tb_instance.instance_id --as tb_temp 
                        left join tb_sensor on tb_sensor.sensor_id = tb_data.sensor_id 
                    where tb_data.sensor_id = %d and sense_time >= '%s' and sense_time <= '%s'
                    ''' %(sensor_id, start_time, end_time)
        
        self.connect()
        result = self.queryAll(sql_str)
        self.close()
        json_inst = {
                      "sensorId": sensor_id,
                      "sensorType": "",
                      "position": "",
                      "values":[],

                     }
        
        for one_row in result:
            sense_time  = one_row[0].strftime('%Y/%m/%d %H:%M:%S')
            position    = one_row[1]
            sensor_type = one_row[2]
            data        = one_row[3]
            
            json_inst['sensorType'] = sensor_type
            json_inst['position']   = position 
            json_inst['values'].append((sense_time, data)) 
        
        json_inst['values'] = tuple(json_inst['values'])
        return json_inst
            
    def update_room_name(self, room_id, room_description):
        """
        修改房间名称
        
        :param room_id: 房间号
        :param room_description: 房间描述
        :rtype: 修改结果，code: 0 成功， -1 失败
        """

        sql_str = u'''
                    update tb_room
                    set room_description = '%s'
                    where room_id = %d
                ''' %(room_description, room_id)
        self.connect()
        self.executeDML(sql_str)
        self.close()
        result = {}
        result['code'] = 0
        result['definition'] = ''
        return result
    
    def update_plant_info(self, plant_id, plant_name):
        """
        修改植物名称
        
        :param plant_id: 植物编号
        :param plant_name: 植物名
        :rtype: 修改结果，code: 0 成功， -1 失败
        """
        sql_str = u'''
                    update tb_plant
                    set plant_name = '%s'
                    where plant_id = %d
                    ''' %(plant_name, plant_id)
        self.connect()
        self.executeDML(sql_str)
        self.close()
        self.load_table()
        return {'code': 0, 'definition': ''}
    
    def all_policy_info(self):
        """
        获取养殖模式简要信息
        
        :rtype: 所有养殖策略简要信息
        """
        sql_str = u'''
            select policy_id, description from tb_policy
            '''
        self.connect()
        temp_list = self.queryAll(sql_str)
        self.close()
        policy_list = []
        for i in temp_list:
            policy_list.append({'policyId':i[0], 'description': i[1]})
        return policy_list
    
    def get_policy(self, policy_id):
        """
        获取指定养殖模式的全部信息
        
        :param policy_id: 策略号
        :rtype: 指定养殖模式的详细信息
        """
        sql_str = u'''
                select description, interval_date, hours, 
                temperature_peak, temperature_valle, humidity_peak, humidity_valle,
                co2_peak, co2_valle, reserved1_peak, reserved1_valle  
                from tb_rule left join tb_policy 
                on tb_rule.policy_id = tb_policy.policy_id
                where tb_policy.policy_id = %d 
                ''' %(policy_id)
        self.connect()
        temp_list = self.queryAll(sql_str)
        self.close()
        policy_info = {}
        policy_info['policyId'] = policy_id
        policy_info['policy'] = []
        try:
            policy_info['description'] = temp_list[0][0]
        except IndexError, e:
            policy_info['description'] = ''
            return policy_info
            
        for i in temp_list:
            temp = {}
            temp['date']        = i[1]
            temp['hour']        = i[2]
            temp['temperature'] = (i[3], i[4])
            temp['humidity']    = (i[5], i[6])
            temp['co2']         = (i[7], i[8])
            temp['brightness']  = (i[9], i[10])
            temp['light']       = ''
            policy_info['policy'].append(temp)
            
        return policy_info 

    def current_policy(self, room_id):
        """
        获取正在执行的养殖策略
        
        :param room_id: 房间号
        :rtype: 指定房间的当前养殖模式的详细信息
        """
        sql_str = u'''
                    select change_time, temperature_peak, temperature_valle, 
                    humidity_peak, humidity_valle, co2_peak, co2_valle, light_color
                    from vw_task
                    where room_id = %d
                    ''' %(room_id)
        self.connect()
        temp_list = self.queryAll(sql_str)
        self.close()
        current_policy = []
        for i in temp_list:
            temp = {}
            temp['changeTime']        = i[0].strftime('%Y/%m/%d %H:%M:%S')
            temp['temperature'] = (i[1], i[2])
            temp['humidity']    = (i[3], i[4])
            temp['co2']         = (i[5], i[6])
            temp['brightness']  = (i[7], i[8])
            temp['light']       = ''
            current_policy.append(temp)
            
        return current_policy
    
    
    def new_policy_instance(self, dict):
        """
        新建全新养殖模式
        
        :param dict: 封装了新建策略必须的信息的字典
        :rtype: 新建结果，code: 0 成功， -1 失败
        """
        policy_id = self.create_policy(dict['description'])
        instance_id = self.create_policy_instance(policy_id, dict['plantName'], dict['roomId'], dict['startAt'])
        for i in range(len(dict['policy'])):
            result = self.create_rule(policy_id, \
                         dict['policy'][i]['date'], \
                         dict['policy'][i]['hour'],\
                         dict['policy'][i]['temperature'][1], \
                         dict['policy'][i]['temperature'][0],\
                         dict['policy'][i]['humidity'][1] ,\
                         dict['policy'][i]['humidity'][0], \
                         dict['policy'][i]['co2'][1], \
                         dict['policy'][i]['co2'][0], \
                         dict['policy'][i]['brightness'][1],\
                         dict['policy'][i]['brightness'][0])
        if policy_id >= 0 and instance_id >= 0 and result >= 0:
            return {'code': 0, 'definition': 'Successful'}, policy_id
        else:
            #TODO: 具体出错位置
            return {'code': -1, 'definition': 'Failed'}
    
    def update_policy_desc(self, policy_id, description):
        """
        修改现存policy的名称
        
        :param policy_id: 待修改的策略号
        :param description: 策略描述
        :rtype: 修改结果，code: 0 成功， -1 失败
        """
        sql_str = '''update tb_policy 
                      set description = '%s' 
                      where policy_id = %d
                      ''' %(description, policy_id)
        self.connect()
        self.executeDML(sql_str)
        self.close()
        return {'code': 0, 'definition': 'Successful'}
    
    def delete_policy(self, policy_id):
        """
        删除指定policy
        
        :param policy_id: 策略号
        :rtype: 删除结果， code: 0 成功， -1 失败
        """
        self.connect()
#         self.executeDML(u'delete from tb_policy_instance where policy_id = %d' %(policy_id))
#         self.executeDML(u'delete from tb_rule where policy_id = %d' %(policy_id))
        self.executeDML(u'delete from tb_policy where policy_id = %d' %(policy_id))
        self.close()
        return {'code': 0, 'definition': 'Successful'}
        
if __name__ == '__main__':
    host = db_conn_info['HOST']
    db_name = db_conn_info['DATABASE']
    user = db_conn_info['USER']
    password = db_conn_info['PASSWORD']
    temp = DbOperator(host, db_name, user, password)
    temp.test_connection()
    
#     for i in range(10):
#         temp.insert_data(2, datetime.now().strftime('%Y-%m-%d'), 12.0, 12.1, 12.2, 12.3)
#         print "now is instance: %d" %i
     
#     print temp.get_room_info(1) 
#     print temp.get_all_room()
#      
    print temp.get_time_reange_data(1, '2014/03/31 09:56:01.000', '2014/04/04 09:56:31.000')
#     print temp.all_policy_info()
#     print temp.get_policy(1)
#     print temp.current_policy(1)
     
#     print temp.update_plant_info(1, 'strowberry')
#     print temp.update_room_name(2, 'left_second')
#     print temp.update_policy_desc(1, 'second_test')
#      
#     dict = {
#             "roomId" : 1,
#             "description": 'forth',
#             "plantName": 'stowberry',
#             "policy": [{
#                             "date" : 1,
#                             "hour" : 12,
#                             "temperature": (10, 20),
#                             "humidity":  (20, 30),
#                             "co2":  (30, 40),
#                             "lightColor": "white",
#                         },
#                        {
#                             "date" : 1,
#                             "hour" : 12,
#                             "temperature": (11, 21),
#                             "humidity":  (21, 31),
#                             "co2":  (31, 41),
#                             "lightColor": "blue",
#                         },
#                        {
#                             "date" : 1,
#                             "hour" : 12,
#                             "temperature": (12, 22),
#                             "humidity":  (22, 32),
#                             "co2":  (32, 42),
#                             "lightColor": "yellow",
#                         },],
#             "startAt":"2014/01/03 16:07",
#             }
#  
#     print temp.new_policy_instance(dict)
#     print temp.delete_policy(14)
#       
#     
#     temp.transfor_absolute_time('2000-1-1 1:1:0')

#     print temp.get_latest_data(1)
#     
#     print temp.certain_sensor_time_range_data(129, '2014/03/31 09:56:01.000', '2014/03/31 09:56:31.000')
    
#     print temp.get_all_room()
