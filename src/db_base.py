#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from db_env import *

class MssqlConnection:
    def __init__(self,):
        #: 服务器地址
        self.host = db_conn_info['HOST']
        #: 数据据库名称
        self.db_name = db_conn_info['DATABASE']
        #: 登录用户
        self.user = db_conn_info['USER']
        #: 登录密码
        self.password = db_conn_info['PASSWORD']
        #: 数据库连接句柄 
        self.handler = ''
        #: 连接游标
        self.cursor = ''

        #: 植物表对象
        self.plant_dict = {}
        #:
        self.plant_name2id = {}
        self.plant_id2name = {}
        #: 传感器表对象
        self.sensor_dict = {}
        self.sensor_name2id = {}
        self.sensor_id2name = {}
        #: 房间表对象
        self.room_dict = {}
        #:
        self.room_desc2id = {}
        self.room_id2desc = {}
        #: 控制器ID与房间号映射
        self.controller_dict = {}

        self.load_table()

    def connect(self):
        """
        建立数据库连接
        """
        if self.handler == '':
            #log_msg = 'In connect-- host: %s, user: %s, password: %s, dbName: %s' %(self.host, self.user, self.password, self.db_name)
            #log_handler.debug(log_msg)
            self.handler = pyodbc.connect(driver='{SQL Server}', server=self.host, \
                                          database=self.db_name, uid=self.user, pwd=self.password, ansi = True)#, unicode_results = True)
            self.cursor = self.handler.cursor()

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
        :rtype: 成功返回生效的数据条数， 失败返回 ERR
        """
        try:
            cnt = self.cursor.execute(sql_str).rowcount
            self.handler.commit()
            return cnt
        except Exception, e:
            log_msg = str(e)
#             log_handler.error(log_msg)
#             print log_msg
            return ERR


    def load_table(self):
        """
        将数据库中部分表加载到内存
        """
        self.connect()

        sql_str = 'select room_id, room_description from tb_room'
        query_list = self.queryAll(sql_str)
        for i in query_list:
            self.room_dict[i[0]] = i[1]
            self.room_desc2id[i[1]] = i[0]
            self.room_id2desc[i[0]] = i[1]

        sql_str = 'select plant_id, plant_name from tb_plant'
        query_list = self.queryAll(sql_str)
        for i in query_list:
            temp = TablePlant()
            temp.plant_id      = i[0]
            temp.plant_name    = i[1]
            self.plant_dict[temp.plant_name] = temp

            self.plant_name2id[i[1]] = i[0]
            self.plant_id2name[i[0]] = i[1]

        sql_str = 'select sensor_id, sensor_type, room_id, state from tb_sensor'
        query_list = self.queryAll(sql_str)
        for i in query_list:
            temp = TableSensor()
            temp.sensor_id      = i[0]
            temp.sensor_name    = i[1]
            temp.room_id        = i[2]
            temp.state          = i[3]

            self.sensor_dict[temp.sensor_name] = temp
            self.sensor_name2id[temp.sensor_name] = temp.sensor_id
            self.sensor_id2name[temp.sensor_id] = temp.sensor_name

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

    def transfor_absolute_time(self, state = POLICY_RUNNING):
        """
        将执行策略的相对时间转换为绝对时间

        :param start_time:  实例最早有效时间
        :rtype: 成功  0 ， 失败 -1
        """
        self.connect()
        self.executeDML("delete from tb_absolute_time")
        instance_list = []

        sql_str = 'select distinct room_id from tb_policy_instance where state >= %d' %(state)
        room_list = self.queryAll(sql_str)
        for room in room_list:
            sql_str = '''select top 1 policy_instance_id, policy_id, plant_id, room_id, start_time from tb_policy_instance
                        where room_id = %d and state >= %d order by state, start_time, policy_instance_id''' %(room[0], state)
            new_instance = self.queryAll(sql_str)
            temp = PolicyInstance()
            temp.instance_id = new_instance[0][0]
            temp.policy_id   = new_instance[0][1]
            temp.plant_id    = new_instance[0][2]
            temp.room_id     = new_instance[0][3]
            temp.start_time  = new_instance[0][4]
            instance_list.append(temp)

        for i in instance_list:
            sql_str = u"""
                        select rule_id, interval_date, hours from tb_rule
                        where policy_id = %d
                        """ %(i.policy_id)
            rst = self.queryAll(sql_str)
            if len(rst) == 0:
                sql_str = 'update tb_policy_instance set state = %d where policy_instance_id = %d' %(POLICY_OLD, i.instance_id)
                self.executeDML(sql_str)

#                 log_msg = 'Got one empty policy, which has been updated to OLD directly !'
#                 log_handler.debug(log_msg)
                continue

            absolute_time_list = []

            first_rule = AbsoluteTime()
            # 获得最后一项规则号，此目的为将最后一条rule_id与次最后的rule_id相同。
            first_rule.rule_id = rst[0][0]
            first_rule.instance_id = i.instance_id
            first_rule.change_time = i.start_time
            absolute_time_list.append(first_rule)

            count = timedelta(days = 0)
            for j in rst[:-1]:
                count += timedelta(days = j[1], hours = j[2])
                change_time = i.start_time + count
                aaa = AbsoluteTime()
                #TODO: 雷区, 策略内的rule在被建立时，其rule_id未必总是连续在一起的
                aaa.rule_id = j[0] + 1
                aaa.instance_id = i.instance_id
                aaa.change_time = change_time
                absolute_time_list.append(aaa)

            count += timedelta(days = rst[-1:][0][1], hours = rst[-1:][0][2])
            change_time = i.start_time + count
            last_rule = AbsoluteTime()
            # 获得最后一项规则号，此目的为将最后一条rule_id与次最后的rule_id相同。
            last_rule.rule_id = rst[-1:][0][0]
            last_rule.instance_id = i.instance_id
            last_rule.change_time = change_time
            absolute_time_list.append(last_rule)

            for j in absolute_time_list:
                sql_str = "insert into tb_absolute_time(rule_id, policy_instance_id, change_time) values(%d, %d, '%s')" %(j.rule_id, j.instance_id, j.change_time)
                try:
                    self.executeDML(sql_str)
                except pyodbc.IntegrityError, e:
                    continue
            sql_str = 'update tb_policy_instance set state = %d where policy_instance_id = %d' %(POLICY_RUNNING, i.instance_id)
            self.executeDML(sql_str)
        self.close()
#         log_msg = "All policy in all room is all ready !"
#         log_handler.debug(log_msg)

    def transfor_room_absolute_time(self, room_id, state = POLICY_RUNNING):
        """
        将数据库中策略的相对时间转换为绝对时间

        :param room_id: 房间号
        :param state: 更改后的策略状态
        :rtype: SUC / FAI / ERR
        """
        self.connect()

        # 查询新策略相关信息
        sql_str = '''select top 1 policy_instance_id, policy_id, plant_id, room_id, start_time from tb_policy_instance
                        where room_id = %d and state >= %d order by state, start_time, policy_instance_id''' %(room_id, state)
        new_instance = self.queryAll(sql_str)

        if len(new_instance) == 0:
            # 无新策略
#             log_msg = 'No new policy to be executed in room: %d' %room_id
#             log_handler.debug(log_msg)
            return FAI

        temp = PolicyInstance()
        temp.instance_id = new_instance[0][0]
        temp.policy_id   = new_instance[0][1]
        temp.plant_id    = new_instance[0][2]
        temp.room_id     = new_instance[0][3]
        temp.start_time  = new_instance[0][4]

        # 查询新策略的执行规则
        sql_str = u'''
                    select rule_id, interval_date, hours from tb_rule
                    where policy_id = %d
                    ''' %(temp.policy_id)
        rst = self.queryAll(sql_str)

        if len(rst) == 0:
            # 此时有新策略，但该策略的执行规则为空
            sql_str = 'update tb_policy_instance set state = %d where policy_instance_id = %d' %(POLICY_OLD, temp.instance_id)
            self.executeDML(sql_str)
#             log_msg = 'Got one empty policy, which has been updated to OLD directly !'
#             log_handler.debug(log_msg)
            return FAI

        # 结合开始时间，将特定策略的相对时间转换为绝对时间
        absolute_time_list = []

        # 获得最后一项规则号，此目的为将最后一条rule_id与次最后的rule_id相同。
        first_rule = AbsoluteTime()
        first_rule.rule_id = rst[0][0]
        first_rule.instance_id = temp.instance_id
        first_rule.change_time = temp.start_time
        absolute_time_list.append(first_rule)

        count = timedelta(days = 0)
        for j in rst[:-1]:
            count += timedelta(days = j[1], hours = j[2])
            change_time = temp.start_time + count
            aaa = AbsoluteTime()
            aaa.rule_id = j[0] + 1
            aaa.instance_id = temp.instance_id
            aaa.change_time = change_time
            absolute_time_list.append(aaa)

        count += timedelta(days = rst[-1:][0][1], hours = rst[-1:][0][2])
        change_time = temp.start_time + count
        last_rule = AbsoluteTime()
        # 获得最后一项规则号，此目的为将最后一条rule_id与次最后的rule_id相同。
        last_rule.rule_id = rst[-1:][0][0]
        last_rule.instance_id = temp.instance_id
        last_rule.change_time = change_time
        absolute_time_list.append(last_rule)

        # 删除当前房间内的绝对时间策略
        sql_str1 = 'select distinct policy_instance_id from vw_task where room_id = %d' %(room_id)
        sql_str2 = '''select top 1 policy_instance_id from tb_policy_instance
                     where room_id = %d
                     order by state, start_time, policy_instance_id''' %(room_id)
        result1 = self.queryAll(sql_str1)
#         result2 = self.queryAll(sql_str2)
        if len(result1) > 0:
            policy_instance_id = result1[0][0]
            sql_str = 'delete from tb_absolute_time where policy_instance_id = %d' %(policy_instance_id)
            self.executeDML(sql_str)
#             log_msg = 'Policy instance :%d delete from tb_absolute_time, for new instance being added to it !' %(policy_instance_id)
#             log_handler.debug(log_msg)

        # 插入新策略的绝对时间规则
        for j in absolute_time_list:
            sql_str = "insert into tb_absolute_time(rule_id, policy_instance_id, change_time) values(%d, %d, '%s')" %(j.rule_id, j.instance_id, j.change_time)
            try:
                self.executeDML(sql_str)
            except pyodbc.IntegrityError, e:
                continue
#         log_msg = 'One new policy instance [ID: %d]applied in room :%d, using policy id: %d' %(temp.instance_id, temp.room_id, temp.policy_id)
#         log_handler.debug(log_msg)
        # 将策略实例状态改为运行态
        sql_str = 'update tb_policy_instance set state = %d where policy_instance_id = %d' %(POLICY_RUNNING, absolute_time_list[0].instance_id)
        self.executeDML(sql_str)

        self.close()

    def new_plant(self, plant_name):
        """
        新建种植植物

        :param plant_name: 植物名称
        :rtype: 成功返回插入条数， 失败返回 ERR
        """
        sql_str = 'insert into tb_plant(plant_name) values(%s)' %(plant_name)
        self.connect()
        result = self.executeDML(sql_str)
        self.close()
        return result

    def insert_room(self, room_id, room_description):
        """
        新建房间

        :param room_id: 植物名称
        :param room_description: 房间描述
        :rtype: 成功返回插入条数， 失败返回 ERR
        """
        sql_str = 'insert into tb_room(room_description) values(%s)' %(room_description)
        self.connect()
        result = self.executeDML(sql_str)
        self.close()
        return result

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
        sql_insert = '''insert into tb_sensor(sensor_id, sensor_type, room_id, position, state)
                    values(%d, '%s', %d, '%s', %d)''' %(sensor_id, sensor_type, room_id, position, state)
        sql_update = '''update tb_sense
                        set sensor_type = '%s',
                        set room_id = %d,
                        set position = %s,
                        set state = %d
                        where sensor_id = %d
                    ''' %(sensor_type, room_id, position, state, sensor_id)
        try:
            self.connect()
            self.executeDML(sql_insert)
            return SUC
        except Exception,err:
            try:
                self.connect()
                self.executeDML(sql_update)
                return SUC
            except Exception, e:
                log_msg = 'Insert Sensor Failed'
#                 log_handler.error(log_msg)
#                 log_msg = 'Insert Sensor Failed: \n%s' %str(e)
                return ERR
        finally:
            self.close()

    def update_sensor(self,  sensor_id, room_id, new_room_id, sensor_type, position = '', state = ON):
        """
        更改传感器信息
        """
        sql_str = '''
                    update tb_sensor
                    set sensor_type = '%s',
                        room_id =
                '''

    def insert_controller(self, controller_id, controller_type, room_id, state = OFF):
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
        #TODO: update
        try:
            self.connect()
            self.executeDML(sql_str)
            self.close()
        except Exception:
            return FAI
        return SUC

    def insert_instance(self, room_id, sense_time):
        try:
            self.connect()
            sql_str = "insert into tb_instance(room_id, sense_time) values(%d, '%s')" %(room_id, sense_time)
            result = self.executeDML(sql_str)
            if result != ERR:
                sql_str = "select instance_id from tb_instance where room_id = %d and sense_time = '%s'" %(room_id, sense_time)
                result = self.queryAll(sql_str)
                self.close()
                return result[0][0]
            else:
                return ERR
        except IndexError:
#             log_msg = 'cannot create instance!'
#             log_handler.error(log_msg)
#             print log_msg
            return FAI

    def insert_sensor_data(self, instance_id, sensor_id, value):
        sql_str = 'insert into tb_data(instance_id, sensor_id, data) values(%d, %d, %f)' %(instance_id, sensor_id, value)
        self.connect()
        self.executeDML(sql_str)
        self.close()
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
            sql_str = "{call sp_insert_sense_data(%d, '%s', %f, %f, %f, %f, %d, %d, %d, %d)}" \
            %(room_id, sense_time, temperature, humidity, co2, light, temperature_id, humidity_id, co2_id, light_id)
#             print sql_str
            self.executeDML(sql_str)
        except KeyError:
            print 'sensor name error'
        self.close()

    def create_policy_instance(self, policy_id, plant_name, room_id, start_time, state = POLICY_NEW):
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
            self.load_table()
            plant_id = self.plant_dict[plant_name].plant_id
#             plant_id = self.queryAll("select plant_id from tb_plant where plant_name ='%s'" %(plant_name))[0][0]
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

    def new_policy_instance(self, dict):
        """
        新建全新养殖模式

        :param dict: 封装了新建策略必须的信息的字典
        :rtype: 新建结果，code: 0 成功， -1 失败
        """
        policy_id = self.create_policy(dict['description'])
        instance_id = self.create_policy_instance(policy_id, dict['plantName'], dict['roomId'], dict['startAt'])
        result = self.create_rule(dict['policy'])
        if policy_id >= 0 and instance_id >= 0 and result >= 0:
            return {'code': 0, 'definition': 'Successful'}, policy_id
        else:
            #TODO: 具体出错位置
            return {'code': -1, 'definition': 'Failed'}

    def update_policy_instance_state(self, room_id, state):
        """
        更改策略实例状态

        :param policy_instance_id: 策略号
        :param state: 状态 
        :rtype: 【尚无】
        """
        self.connect()

        sql_str = 'select distinct policy_instance_id from vw_task where room_id = %d' %(room_id)
        temp = self.queryAll(sql_str)

        if len(temp) == 0:
            log_msg = 'update policy instance state in room: %d to state: %d failed' %(room_id, state)
            return FAI
        policy_instance_id = temp[0][0]

        sql_str = '''
                    update tb_policy_instance
                    set state = %d
                    where policy_instance_id = %d
                ''' %(state, policy_instance_id)
        self.executeDML(sql_str)
        self.close()
#         log_msg = 'Policy instance %d updated to state %d' %(policy_instance_id, state)
#         log_handler.debug(log_msg)

    def delete_policy(self, policy_id):
        sql_str = 'delete from tb_policy where policy_id = %d' %(policy_id)
        self.connect()
        self.executeDML(sql_str)
        self.close()
        return SUC

    def create_rule(self, policy_id, rules):
        """
        插入养殖模式

        :param policy_id: 策略号
        :param rules: 执行规则列表
        :rtype: SUC
        """
        self.connect()
        for one_rule in rules:
            sql_str = u'''insert into tb_rule(
                            policy_id,
                            interval_date,
                            hours,
                            temperature_peak,
                            temperature_valle,
                            humidity_peak,
                            humidity_valle,
                            co2_peak,
                            co2_valle,
                            reserved1_peak,
                            reserved1_valle
                        )values( %d, %d, %d, %f, %f, %f, %f, %f, %f, %f, %f)''' \
                            %(policy_id,\
                             one_rule['date'], \
                             one_rule['hour'], \
                             one_rule['temperature'][1], \
                             one_rule['temperature'][0],\
                             one_rule['humidity'][1], \
                             one_rule['humidity'][0],\
                             one_rule['co2'][1], \
                             one_rule['co2'][0], \
                             one_rule['brightness'][1], \
                             one_rule['brightness'][0]
                        )
            self.executeDML(sql_str)
        self.close()
        return SUC

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
        sql_str = '''
                select top 2 %d, change_time,
                            temperature_valle, temperature_peak,
                            humidity_valle, humidity_peak,
                            co2_valle, co2_peak,
                            light_color, reserved1_valle, reserved1_peak, policy_instance_id
                from vw_task
                where change_time >= '%s' and room_id = %d
                order by change_time
                ''' %(room_id, datetime, room_id)

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

    conn.transfor_absolute_time()
#     temp = conn.get_threshold(1, '2014-01-06 16:07:00')
#     print temp
    conn.test_connection()
#     print temp[0][8]
#     print (temp[1][0], str(temp[1][1]))
