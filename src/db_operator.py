#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from db_base import MssqlConnection
from db_env import *

class DbOperator(MssqlConnection):
    def __init__(self, ):
        MssqlConnection.__init__(self)
    
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
        print 'length = %d' %len(data)
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
        :rtype: 指定养殖模式的详细信息,失败返回FAI
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
    
    def get_policy_instance_now(self, policy_id = None, room_id = None):
        """
        获取中正在执行的实例
        
        :param policy_id:
        :param room_id: 
        :rtype: 指定养殖模式的详细信息,失败返回FAI
        """
        if policy_id != None:
            
            sql_str = u'''
                    select change_time,
                        temperature_peak, temperature_valle, 
                        humidity_peak, humidity_valle,
                        co2_peak, co2_valle,
                        reserved1_peak, reserved1_valle, 
                        light_color, policy_id, room_id
                    from vw_task
                    where vw_task.policy_id = %d
                    order by change_time
                    ''' %(policy_id)
            self.connect()
            temp_list = self.queryAll(sql_str)
            self.close()
            
            the_end = {}
            for i in temp_list:                
                policy_id           = i[10]
                room_id             = i[11]
                if the_end.has_key(room_id):
                    pass
                else:
                    the_end[room_id] = {'roomId' : room_id,
                                    'roomDesc' : self.room_id2desc[room_id],
                                    'policy_id' : policy_id,
                                    'now' : '',
                                    'rules' : []
                                   }
            for i in temp_list:
                temp = {}
                temp['changeTime']  = i[0].strftime('%Y/%m/%d %H:%M:%S')
                temp['temperature'] = (i[1], i[2])
                temp['humidity']    = (i[3], i[4])
                temp['co2']         = (i[5], i[6])
                temp['brightness']  = (i[7], i[8])
                temp['light']       = ''
                room_id             = i[11]
                the_end[room_id]['rules'].append(temp)
                
                if i[0] <= datetime.now():
                    the_end[room_id]['now'] = temp['changeTime']
                    
            end_list = [] 
            for key in the_end.keys():
                end_list.append(the_end[key])
            return end_list
        
        elif room_id != None:
            sql_str = u'''
                    select change_time,
                        temperature_peak, temperature_valle, 
                        humidity_peak, humidity_valle,
                        co2_peak, co2_valle,
                        reserved1_peak, reserved1_valle, 
                        light_color, policy_id, room_id
                    from vw_task
                    where vw_task.room_id = %d
                    order by change_time
                    ''' %(room_id)
            self.connect()
            temp_list = self.queryAll(sql_str)
            self.close()
            
            rule_list = []
            current_instance = {'roomId' : room_id,
                                'roomDesc' : self.room_id2desc[room_id],
                                'now': '',
                                'rules': rule_list,
                              }
            current_rule_time = ''
            policy_id = -1
            for i in temp_list:
                temp = {}
                temp['changeTime']  = i[0].strftime('%Y/%m/%d %H:%M:%S')
                temp['temperature'] = (i[1], i[2])
                temp['humidity']    = (i[3], i[4])
                temp['co2']         = (i[5], i[6])
                temp['brightness']  = (i[7], i[8])
                temp['light']       = ''
                policy_id           = i[10]
                rule_list.append(temp)
                if i[0] <= datetime.now():
                    current_rule_time = temp['changeTime']
            current_instance['policyId'] = policy_id
            current_instance['now'] = current_rule_time
            return [current_instance]
        else:
            return FAI
    
    def get_policy_instance_plan_list(self, policy_id):
        """
        获取计划中的实例
        
        :param policy_id: 策略号
        :rtype: 指定格式的数据
        """
        instance_info = []
        sql_str = ''' select policy_instance_id, room_id, start_time, plant_id from tb_policy_instance 
                        where policy_id = %d and state = %d ''' %(policy_id, POLICY_NEW)
        self.connect()
        instance_list = self.queryAll(sql_str)
        self.close()
        for one_instance in instance_list:
            temp_instance = {}
            temp_instance['policyInstanceId'] = one_instance[0]
            temp_instance['roomDesc'] = self.room_id2desc[one_instance[1]]
            temp_instance['startAt'] = one_instance[2]
            temp_instance['plantName'] = self.plant_id2name[one_instance[3]]
            instance_info.append(temp_instance)
        return instance_info
    
    def get_policy_instance_done_list(self, policy_id):
        """
        获取执行过的实例
        
        :param policy_id: 策略号
        :rtype: 指定格式的数据
        """
        instance_info = []
        sql_str = ''' select policy_instance_id, room_id, start_time, plant_id from tb_policy_instance 
                        where policy_id = %d and state = %d ''' %(policy_id, POLICY_OLD)
        self.connect()
        instance_list = self.queryAll(sql_str)
        self.close()
        for one_instance in instance_list:
            temp_instance = {}
            temp_instance['policyInstanceId'] = one_instance[0]
            temp_instance['roomDesc'] = self.room_id2desc[one_instance[1]]
            temp_instance['startAt'] = one_instance[2]
            temp_instance['plantName'] = self.plant_id2name[one_instance[3]]
            instance_info.append(temp_instance)
        return instance_info
    
    def get_policy_2(self, policy_id):
        """
        获取指定策略的部分信息
        
        :param policy_id: 策略号
        :rtype: 指定格式的策略信息,失败返回 FAI
        """
        policy_info = self.get_policy(policy_id)
        policy_info['rules'] = policy_info['policy']
        policy_info.pop('policy')
        
        policy_info['now']  = []
        policy_info['old']  = []
        policy_info['plan'] = []
        
        self.connect()
        try:
            sql_str = " select policy_instance_id from tb_policy_instance where policy_id = %d and state = %d" %(policy_id, POLICY_RUNNING)
        
            now_instance_list = self.queryAll(sql_str)
            for one_instance in now_instance_list:
                policy_info['now'].append(one_instance[0])
        except IndexError:
            pass
                
        try: 
            sql_str = " select policy_instance_id from tb_policy_instance where policy_id = %d and state = %d " %(policy_id, POLICY_NEW)
            plan_instance_id_list = self.queryAll(sql_str)
            for instance in plan_instance_id_list:
                policy_info['plan'].append(instance[0])
        except IndexError:
            pass
        
        try: 
            sql_str = " select policy_instance_id from tb_policy_instance where policy_id = %d and state = %d " %(policy_id, POLICY_OLD)
            old_instance_id_list= self.queryAll(sql_str) 
            for instance in old_instance_id_list:
                policy_info['old'].append(instance[0])
            return policy_info
        except IndexError:
            return FAI
    
    def current_policy(self, room_id):
        """
        获取正在执行的养殖策略
        
        :param room_id: 房间号
        :rtype: 指定房间的当前养殖模式的详细信息
        """
        sql_str = u'''
                    select change_time, 
                            temperature_peak, temperature_valle, 
                            humidity_peak, humidity_valle, 
                            co2_peak, co2_valle, 
                            reserved1_peak, reserved1_valle, light_color,
                            tb_policy.policy_id, tb_policy.description, vw_task.policy_instance_id
                    from vw_task left join tb_policy_instance on vw_task.policy_instance_id = tb_policy_instance.policy_instance_id
                        left join tb_policy on tb_policy_instance.policy_id = tb_policy.policy_id
                    where vw_task.room_id = %d
                    ''' %(room_id)
        self.connect()
        temp_list = self.queryAll(sql_str)
        self.close()
        rule_list = []
        for i in temp_list:
            temp = {}
            temp['changeTime']        = i[0].strftime('%Y/%m/%d %H:%M:%S')
            temp['temperature'] = (i[1], i[2])
            temp['humidity']    = (i[3], i[4])
            temp['co2']         = (i[5], i[6])
            temp['brightness']  = (i[7], i[8])
            temp['light']       = ''
            rule_list.append(temp)
            
        current_policy = {'pid': temp_list[0][10],
                  'description' : temp_list[0][11],
                  'rules': rule_list,
                  }
            
        return current_policy
    
    def new_policy(self, description, rules = ''):
        """
        创建新策略
        :param description: 策略描述，长度限制  <20字符
        :rtype: 成功返回新建的策略号， 失败返回 -1
        """
        
        if len(description) > 20:
            log_msg = 'description is too long, please make sure the lenght less than 20'
            print 
            return -1
        sql_str = u"insert into tb_policy(description) values('%s')" %(description)
        try:
            self.connect()
            self.executeDML(sql_str)
            sql_str = "select top 1 policy_id from tb_policy where description = '%s' order by policy_id desc" %(description)
            policy_id = self.queryAll(sql_str)[0][0]
            self.close()
            
            if len(rules) > 0:
                self.create_rule(policy_id, rules)
                
            return policy_id
        except KeyboardInterrupt, e:
            print e
            return ERR
    
    def new_policy_instance_2(self, policy_id, plant_name, room_desc, start_time):
        """
        创建新的策略实例
        
        :param policy_id: 策略号
        :param plany_name: 名称
        :param room_desc: 房间描述
        :param start_time: 开始执行时间,格式要求： 2013-12-17 15:45:00 （格式受限于SQLServer）
        :rtype: 成功返回新建的实例号，失败返回 -1， 异常返回 -2
        """
        self.connect()
        try:
            plant_id = self.plant_name2id[plant_name]
        except KeyError:
            self.executeDML("insert into tb_plant(plant_name) values('%s')" %(plant_name))
            self.load_table()
            plant_id = self.plant_name2id[plant_name]
        try:
            room_id = self.room_desc2id[room_desc]
        except KeyError:
            return FAI
#             self.executeDML("insert into tb_room(room_description) values('%s')" %(room_desc))
#             self.load_table()
#             room_id = self.room_desc2id[room_desc]
        try:
            sql_str = '''insert into tb_policy_instance(policy_id, plant_id, room_id, start_time, state) 
                        values(%d, %d, %d, '%s', %d)''' %(policy_id, plant_id, room_id, start_time, POLICY_NEW)
            self.executeDML(sql_str)
            instance_id = self.queryAll('''select top 1 policy_instance_id from tb_policy_instance 
                                            where policy_id = %d order by policy_instance_id desc''' %(policy_id))[0][0]
            self.close()
            return instance_id
        except Exception, e:
            print 'in create_policy_instance: '
            print e
            return ERR
    
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
    
    def update_policy(self, policy_id, rules):
        """
        修改指定策略
        
        :param policy_id: 策略号
        :rules rules: 执行规则
        :rtype: SUC / FAI / ERR
        """
        sql_str = 'delete from tb_rule where policy_id = %d' %(policy_id)
        self.connect()
        self.executeDML(sql_str)
        self.close()
        
        if len(rules) > 0:
            result = self.create_rule(policy_id, rules)
    
    def update_policy_instance(self, policy_instance_id, room_desc, plant_name, start_time):
        """
        更改策略实例信息
        
        :param policy_instance_id: 实例号
        :param room_desc: 房间描述
        :param plant_name: 植物名称
        :param start_time: 开始执行时间
        :rtype: SUC 成功， FAI 失败， ERR 异常
        """
        self.connect()
        try:
            plant_id = self.plant_name2id[plant_name]
            room_id = self.room_desc2id[room_desc]
        except KeyError:
            print 'Some info provited not exist, please check it'
            return FAI
        
        sql_str = '''
            update tb_policy_instance
            set room_id = %d,
                plant_id = %d, 
                start_time = '%s'
            where policy_instance_id = %d
            ''' %(room_id, plant_id, start_time, policy_instance_id)
        self.executeDML(sql_str)
        self.close()
        return SUC
    
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
    
    def delete_policy_instance(self, policy_instance_id):
        sql_str = 'delete from tb_policy_instance where policy_instance_id = %d' %(policy_instance_id)
        self.connect()
        self.executeDML(sql_str)
        self.close()
        return SUC
    
if __name__ == '__main__':
    temp = DbOperator()
    temp.test_connection()
    
#     print temp.current_policy(3)
    print temp.get_policy_2(142) #check
    
    rules = [
             {'co2': (12.0, 12.0), 
              'temperature': (12.0, 12.0), 
              'hour': 1, 
              'brightness': (12.0, 12.0), 
              'light': '', 
              'humidity': (12.0, 12.0), 
              'date': 0
              }, 
             {'co2': (12.0, 12.0), 
              'temperature': (12.0, 12.0), 
              'hour': 1, 
              'brightness': (12.0, 12.0), 
              'light': '', 
              'humidity': (12.0, 12.0), 
              'date': 0
              }, 
            {'co2': (12.0, 12.0), 
             'temperature': (12.0, 12.0), 
             'hour': 1, 
             'brightness': (12.0, 12.0), 
             'light': '', 
             'humidity': (12.0, 12.0), 
             'date': 0}
        ]
#     temp.new_policy(u'新策略', rules)    # check
#     temp.update_policy(124, rules)     # check
#     temp.new_policy_instance_2(124, 'mongou', 'left_second', '2014-04-15 12:12:00.000') #check 
#     temp.update_policy_instance(106, 'left_first', 'xianggu', '2014-04-16 12:12:00.000') #check
#     temp.delete_policy_instance(106) #check
#     print temp.get_policy_instance_now(142, None) #check
#     print temp.get_policy_instance_plan_list(142) # check
#     print temp.get_policy_instance_done_list(53) # check

    len(temp.get_time_reange_data(1,'2014-04-28 1:1:1', '2014-04-28 20:10:00'))
    print 'search end'
[
  {'roomDesc': u'left_second', 
   'now': '2014/04/22 15:12:00', 
   'roomId': 2, 
   'policy_id': 142,
   'rules': [
            {'changeTime': '2014/04/22 11:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)},
            {'changeTime': '2014/04/22 12:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}, 
            {'changeTime': '2014/04/22 14:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}, 
            {'changeTime': '2014/04/22 15:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}, 
            {'changeTime': '2014/04/22 17:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}, 
            {'changeTime': '2014/04/22 18:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}, 
            {'changeTime': '2014/04/22 20:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}, 
            {'changeTime': '2014/04/22 21:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}, 
            {'changeTime': '2014/04/22 23:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}
        ], 
   
    }, 
    {   
        'roomDesc': u'one month', 
        'now': '2014/04/22 15:12:00', 
        'roomId': 3, 
        'policy_id': 142,
        'rules': [
             {'changeTime': '2014/04/22 11:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}, 
             {'changeTime': '2014/04/22 12:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}, 
             {'changeTime': '2014/04/22 14:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}, 
             {'changeTime': '2014/04/22 15:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}, 
             {'changeTime': '2014/04/22 17:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}, 
             {'changeTime': '2014/04/22 18:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}, 
             {'changeTime': '2014/04/22 20:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}, 
             {'changeTime': '2014/04/22 21:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}, 
             {'changeTime': '2014/04/22 23:12:00', 'co2': (200.0, 100.0), 'temperature': (200.0, 100.0), 'brightness': (200.0, 100.0), 'light': '', 'humidity': (200.0, 100.0)}
             ], 
     }
]
