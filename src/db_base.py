#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from db_env import *

class MssqlConnection:  
    def __init__(self, serverIp = db_conn_info['HOST'], dbName = db_conn_info['DATABASE'], \
                 uid = db_conn_info['USER'], pwd = db_conn_info['PASSWORD']):
        #: 服务器地址
        self.host = serverIp
        #: 数据据库名称
        self.db_name = dbName
        #: 登录用户
        self.user = uid
        #: 登录密码
        self.password = pwd    
        #: 数据库连接句柄  
        self.handler = ''
        #: 连接游标
        self.cursor = ''
        
        #: 植物表对象
        self.plant_dict = {}
        #: 传感器表对象
        self.sensor_dict = {}
        #: 房间表对象
        self.room_dict = {}
        #: 控制器ID与房间号映射
        self.controller_dict = {}
        
        self.load_table()

    def connect(self):
        """
        建立数据库连接
        """
        if self.handler == '':
            self.handler = pyodbc.connect(driver='{SQL Server}', server=self.host, \
                                          database=self.db_name, uid=self.user, pwd=self.password, unicode_results = True)  
            self.cursor=self.handler.cursor()
    
    def close(self): 
        """
        关闭数据库连接
        
        :rtype: 0 成功， -1 失败
        """
        if self.cursor:   
            self.cursor.close()  
            self.cursor = ''
        if self.handler:  
            self.handler.close()
            self.handler = ''
        return 0
  
    def queryAll(self, sql_str):  
        """
        获取全部查询结果 
        
        :param sql_str: 待执行的SQL语句
        :rtype: 查询结果              
        """   
        self.cursor.execute(sql_str)  
        return self.cursor.fetchall()  
  
    def querySome(self, sql_str, maxcnt):  
        """
        获取前maxcnt条查询结果
         
        :param sql_str: 待执行的SQL语句
        :param maxcnt: 返回限制的行数
        :rtype: 查询结果
        """  
        self.cursor.execute(sql_str)  
        return self.cursor.fetchmany(maxcnt)  
  
    def queryPage(self, sql_str, skip_cnt, page_size):  
        """ 
        获取分页查询结果
        
        :param sql_str: 待执行的SQL语句 
        :param skip_cnt:
        :param page_size:
        :rtype: 
        """  
        self.cursor.execute(sql_str)  
        self.cursor.skip(skip_cnt)  
        return self.cursor.fetchmany(page_size)  
  
    def count(self,sql_str):  
        """
        获取查询条数
        
        :param sql_str: 待执行的SQL语句 
        :rtype: 查询条数
        """  
        self.cursor.execute(sql_str)  
        return self.cursor.fetchone()[0]  
  
    def executeDML(self, sql_str):  
        """
        执行DML语句，包括增删改
        
        :param sql_str: 待执行的SQL语句 
        :rtype: 成功返回生效的数据条数， 失败返回-1 
        """  
        cnt = self.cursor.execute(sql_str).rowcount
        self.handler.commit()
        return cnt
    
    
    def load_table(self):
        """
        将数据库中部分表加载到内存
        """
        self.connect()
        sql_str = 'select plant_id, plant_name from tb_plant'
        query_list = self.queryAll(sql_str)
        for i in query_list:
            temp = TablePlant()
            temp.plant_id      = i[0]
            temp.plant_name    = i[1]
            self.plant_dict[temp.plant_name] = temp
        
        sql_str = 'select sensor_id, sensor_type, room_id, state from tb_sensor'
        query_list = self.queryAll(sql_str)
        for i in query_list:
            temp = TableSensor()
            temp.sensor_id      = i[0]
            temp.sensor_name    = i[1]
            temp.room_id        = i[2]
            temp.state          = i[3]
            self.sensor_dict[temp.sensor_name] = temp
        
        sql_str = 'select controller_id, room_id, controller_type from tb_controller'
        query_list = self.queryAll(sql_str)
        #TODO: 这里可定有问题，每个房间有多个控制器，但是否
        for i in query_list:
            self.controller_dict[i[1]] = {i[2]: i[0]}
            
        self.close()
        
    def test_connection(self):
        try:
            self.connect()
            query_list = self.queryAll("SELECT 'SQLServer Connection Successful'")
            print query_list
        except Exception, e:
            print e
            return str(e)
        finally:
            self.close()
    
    def transfor_absolute_time(self, start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
        """
        将执行策略的相对时间转换为绝对时间
        
        :param start_time:  实例最早有效时间
        :rtype: 成功  0 ， 失败 -1
        """
        self.connect()
        self.executeDML("delete from tb_absolute_time")
        instance_list = []
        sql_str = "select * from tb_policy_instance where start_time >= '%s'" %(start_time)
        policy_instance_list=self.queryAll(sql_str)
        
        for i in policy_instance_list:
            temp = PolicyInstance()
            temp.instance_id = i[0]
            temp.policy_id   = i[1]
            temp.plant_id    = i[2]
            temp.room_id     = i[3]
            temp.start_time  = i[4]
            instance_list.append(temp)
        
        for i in instance_list:
#             print '\n======================================='
#             print 'instance_id = ', i.instance_id, 'policy_id = ', i.policy_id, 'start_time = ', i.start_time
#             print '======================================='
            sql_str = u""" 
                        select rule_id, interval_date, hours from tb_rule
                        where policy_id = %d
                        """ %(i.policy_id)
            rst = self.queryAll(sql_str)
            import datetime
            count = datetime.timedelta(days = 0)
            absolute_time_list = []
            for j in rst:
                count += datetime.timedelta(days = j[1], hours = j[2])
                change_time = i.start_time + count
                aaa = AbsoluteTime()
                aaa.rule_id = j[0]
                aaa.instance_id = i.instance_id
                aaa.change_time = change_time
                absolute_time_list.append(aaa)
            for j in absolute_time_list:
#                 print 'instance_id = ', j.instance_id, 'rule_id = ', j.rule_id, 'change_time = ', j.change_time
#                 print '---------------------------'
                sql_str = "insert into tb_absolute_time(rule_id, policy_instance_id, change_time) values(%d, %d, '%s')" %(j.rule_id, j.instance_id, j.change_time)
#                 print sql_str
                try:
                    self.executeDML(sql_str)
                except pyodbc.IntegrityError, e:
                    continue
        self.close()
        print "Translate to Absolute Time Done!"
    
    
    def insert_sensor(self, sensor_id, sensor_type, room_id, position = '', state = ON):
        """
        插入传感器信息
        
        :param sensor_id: 传感器ID 整型
        :param sensor_type: 传感器类型 字符串
        :param room_id: 房间ID 整型
        :param position: 传感器位置 
        :param state: 传感器当前状态
        :rtype: SUC 成功， FAI 失败， ERR 异常
        """
        sql_str = '''insert into tb_sensor(sensor_id, sensor_type, room_id, position, state) 
                    values(%d, '%s', %d, '%s', %d)''' %(sensor_id, sensor_type, room_id, position, state)
        try:
            self.connect()
            self.executeDML(sql_str)
            self.close()
        except Exception:
            return FAI
        return SUC
    
    def insert_controller(self, controller_id, controller_type, room_id, state = ON):
        """
        插入控制器信息
        
        :param controller_id: 控制器ID
        :param controller_type: 控制器类型 字符串
        :param room_id: 房间ID
        :param state: 传感器当前状态
        :rtype: SUC 成功， FAI 失败， ERR 异常
        """
        sql_str = '''insert into tb_controller(controller_id, controller_type, room_id, state) 
                    values(%d, '%s', %d, %d)''' %(controller_id, controller_type, room_id, state)
        try:
            self.connect()
            self.executeDML(sql_str)
            self.close()
        except Exception:
            return FAI
        return SUC
        
    def insert_data(self, room_id, sense_time, temperature, humidity, co2, light, \
                    temperature_id = -1, humidity_id = -1, co2_id = -1, light_id = -1):
        """
        插入采集数据接口
        
        :param room_id: 房间号
        :param sense_time: 采集时间
        :param temperature: 温度
        :param humidity: 湿度
        :param co2: 二氧化碳浓度
        :param light: 光照
        :rtype: 成功返回 1， 失败返回错误信息
        """
        if temperature_id < 0 or humidity < 0 or co2_id < 0 or light_id < 0:
            temperature_id = self.sensor_dict['temperature'].sensor_id
            humidity_id = self.sensor_dict['humidity'].sensor_id
            co2_id = self.sensor_dict['co2'].sensor_id
            light_id = self.sensor_dict['light'].sensor_id
            
        self.connect()
#         start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            sql_str = u"{call sp_insert_sense_data(%d, '%s', %f, %f, %f, %f, %d, %d, %d, %d)}" \
            %(room_id, sense_time, temperature, humidity, co2, light, temperature_id, humidity_id, co2_id, light_id) 
            self.executeDML(sql_str)
        except KeyError: 
            print 'sensor name error'
        self.close()
    
    def create_policy(self, description):
        """
        创建新策略
        :param description: 策略描述，长度限制  <20字符
        :rtype: 成功返回新建的策略号， 失败返回 -1
        """
        
        if len(description) > 20:
            return -1
        sql_str = "insert into tb_policy(description) values('%s')" %(description)
        try:
            self.connect()
            self.executeDML(sql_str)
            sql_str = "select top 1 policy_id from tb_policy where description = '%s' order by policy_id desc" %(description)
            temp = self.queryAll(sql_str)[0][0]
            self.close()
            return temp
        except Exception, e:
            print e
            return -1
            
    def create_policy_instance(self, policy_id, plant_name, room_id, start_time, state = 2):
        """
        创建新的策略实例
        
        :param policy_id: 策略号
        :param plany_name: 名称
        :param room_id: 房间号
        :param start_time: 开始执行时间,格式要求： 2013-12-17 15:45:00 （格式受限于SQLServer）
        :rtype: 成功返回新建的实例号，失败返回-1
        """
        self.connect()
        try:
            plant_id = self.plant_dict[plant_name].plant_id
        except KeyError:
            self.executeDML("insert into tb_plant(plant_name) values('%s')" %(plant_name))
            plant_id = self.queryAll("select plant_id from tb_plant where plant_name ='%s'" %(plant_name))[0][0]
            self.load_table()
        
        try:
            sql_str = '''insert into tb_policy_instance(policy_id, plant_id, room_id, start_time, state) 
                        values(%d, %d, %d, '%s', %d)''' %(policy_id, plant_id, room_id, start_time, state)
            self.executeDML(sql_str)
            instance_id = self.queryAll('''select top 1 policy_instance_id from tb_policy_instance 
                                            where policy_id = %d order by policy_instance_id desc''' %(policy_id))[0][0]
            self.close()
            return instance_id
        except Exception, e:
            print 'in create_policy_instance: '
            print e
            return -1
    
    def create_rule(self, policy_id, interval_date, hours, temperature_peak, temperature_valle, 
                    humidity_peak, humidity_valle, co2_peak, co2_valle, light_color):
        """
        插入养殖模式
        
        :param policy_id: 策略号
        :param interval_date: 间隔天数
        :param hours: 间隔小时数
        :param temperature_peak: 温度峰值
        :param temperature_valle: 温度谷值
        :param humidity_peak: 湿度峰值
        :param humidity_valle: 湿度谷值
        :param co2_peak: 二氧化碳浓度峰值
        :param co2_valle: 二氧化碳浓度谷值
        :param light_color: 光色
        :rtype: 
        """
        self.connect()
        sql_str = u'''insert into tb_rule(policy_id, interval_date, hours, temperature_peak, temperature_valle,
        humidity_peak, humidity_valle, co2_peak, co2_valle, light_color)
        values( %d, %d, %d, %f, %f, %f, %f, %f, %f, '%s')''' \
        %(policy_id, interval_date, hours, temperature_peak, temperature_valle,\
          humidity_peak, humidity_valle, co2_peak, co2_valle, light_color)
        self.executeDML(sql_str)
        self.close()
        
        return 0
    
    def view_controller(self, controller_id):
        """
        查看控制器状态
        
        :param controller_id:控制器ID
        :rtype:返回控制器状态，整数
        """
        self.connect()
        sql_str = ''' select state from tb_controller where controller_id = %d''' %(controller_id)
        state = self.queryAll(sql_str)
        self.close()
        return state[0][0]
    
    def update_controller(self, controller_id, state):
        """
        更改控制器状态
        
        :param controller: 控制器ID
        :param state: 状态
        :rtype: 0【待定】
        """
        self.connect()
        sql_str = '''update tb_controller set state = %d where controller_id = %d''' %(state, controller_id)
        self.executeDML(sql_str)
        self.close()
        return 0
    
    def get_threshold(self, room_id, datetime):
        """
        此函数可以获得指定房间的制定时刻的环境限定范围，主要为head.h文件内的threshold队列变量服务
        
        :param datetime: 查询时间
        :param room_id: 房间号
        :rtype: 包含了两个限定范围的元组，
        """
        #TODO: 这里我们假设tb_absolute_time 中，一个房间只能有一种策略在执行，且目前版本，在系统初始化时务必这样，否则将混乱
        sql_str = u'''
                select top 2 room_id, change_time, 
                            temperature_valle, temperature_peak,  
                            humidity_valle, humidity_peak, 
                            co2_valle, co2_peak, 
                            light_color
                from vw_task
                where change_time >= '%s' and room_id = %d
                order by change_time
                ''' %(datetime, room_id)
        self.connect()
        temp = self.queryAll(sql_str)
        self.close()
        return temp
        
if __name__ == "__main__":  
    serverIp = db_conn_info['HOST']
    dbName = db_conn_info['DATABASE']
    uid = db_conn_info['USER'] 
    pwd = db_conn_info['PASSWORD'] 
#     conn=MssqlConnection(serverIp,dbName,uid,pwd)
    conn=MssqlConnection()
    
    temp = conn.get_threshold(1, '2014-01-06 16:07:00')
    print temp[0][8]
    print (temp[1][0], str(temp[1][1]))