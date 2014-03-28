#!/usr/bin/env python
# -*- coding: utf-8 -*-

from head import *
from task_list import global_task_list
from arm_frame_main import ArmFrameMain
from django_frame_main import DjangoFrameMain

class SkNode():
    """
    连接对象类
    """
    #: 连接句柄
    handler= ''
    #: 最终活跃时间
    last_time  = ''
    #: 固有锁
    mylock = threading.Lock()

    def fileno(self):
        """
        获取连接句柄文件描述符，因为在调用select系统函数时，至少有一个参数,不为空且必须为整型或有fileno()方法

        :rtype: 返回内部连接句柄文件描述符
        """
        return self.handler.fileno()

class SocketList:
    """
    作为上行线程和下行线程通用的套接字管理类，为集合了套接字连接队列的建立和管理等功能
    """

    def __init__(self, FrameMain, client_list):

        #: 上下行线程区分依据
        self.FrameMain = FrameMain
        #: 套接字连接队列
        self.client_list = client_list
        #: 标记当前线程名称
        self.thread_name = ''
        if FrameMain == ArmFrameMain:
            #: 套接字连接字典
            self.client_dict = arm_client_dic
            self.thread_name = 'RAM'
        else:
            #: 套接字连接字典
            self.client_dict = django_client_dic
            self.thread_name = 'Django'

    def init(self, server_addr, listen_num):
        """
        初始化
        :param server_addr: 服务开启地址，eg：SERVER_ADDR = ('127.0.0.1', 9998)
        :param listen_num: 最大同时监听数
        :rtypee: return 0 if succeed or -1 if failed
        """
        #: 服务端口
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.setblocking(False)
        # set option reuseable
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR  , 1)

        self.server.bind(server_addr)
        self.server.listen(listen_num)
        self.server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        serv = SkNode()
        serv.handler = self.server
        #: sockets from which we except to read
        self.client_list.append(serv)
        self.client_dict[self.server.fileno()] = serv
        return 0

    def manage_list(self, stopEvent, param, ):
        """
        套接字连接管理方法

        :param param: 【未用】
        :rtype: return 0 if scucess, or -1 if something wrong
        """
        log_msg = 'Thread ' + self.thread_name + ' Server is Ready'
#         log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)
        log_handler.work(log_msg)
        while not stopEvent.isSet():
            try:
                sk_node, readable, writable, exceptional = ('', '', '', '')
                while not stopEvent.isSet() and self.client_list:
                    readable , writable , exceptional = select.select(self.client_list, [], [], SELECT_TIMEOUT)
                    # When timeout reached , select return three empty lists
                    if not (readable or writable or exceptional) :
#                         log_msg = "%s Time out ! clinet_list length is %d" %(self.thread_name, len(self.client_list))
#                         log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)
                        continue
                    for sk_node in readable :
                        if sk_node.handler is self.server:
                            connection, client_address = sk_node.handler.accept()
                            connection.setblocking(1)
                            connection.settimeout(RECV_TIMEOUT)

                            log_msg = "[ %s ] One Connection Established From :%s, Fileno = %d" %(self.thread_name, str(client_address), connection.fileno())
#                             log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)
                            log_handler.work(log_msg)

                            client = SkNode()
                            client.handler = connection
                            client.last_time = datetime.now()
                            client.mylock.acquire()
                            self.client_list.append(client)
                            self.client_dict[connection.fileno()] = client
                            client.mylock.release()
                        else:
#                             temp = sk_node.handler.recv(1024)
#                             print temp
#                             sk_node.handler.send(temp)
#                             self.dead_client_dealer(sk_node)
                            one_client_dealer = self.FrameMain(sk_node)
#                             print "client_List = %s, ram_client_list = %s" %(self.client_list, self.ram_client_list)
                            result = one_client_dealer.main_receivor()
                            if result == SUC :
                                log_msg = "[ %s ] One frame solved from fileno %d " %(self.thread_name, sk_node.fileno())
                                log_handler.work(log_msg)
                                print "=========================================== \n"

                            elif result == ERR :
                                log_msg = "[ %s ] One connection Timeout from fileno %d " %(self.thread_name, sk_node.fileno())
                                log_handler.work(log_msg)
#                                 log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)

                                self.dead_client_dealer(sk_node)
                                log_msg = "Now the connection list is : "
                                for i in range(len(self.client_list)):
                                    log_msg += str(self.client_list[i].fileno()) + ', '
                                log_handler.work(log_msg)
                            elif result == FAI:
                                continue
                    for sk_node in exceptional:
                        print " exception condition on ", sk_node.getpeername()
                        #: stop listening for input on the connection
                        self.client_list.remove(sk_node)
                        self.client_dict.pop(sk_node.fileno())
                        sk_node.close()
            except socket.error, e:
                log_msg = "[ %s ] Socket error from fileno : %d " %(self.thread_name, sk_node.fileno())
                log_handler.error(log_msg)
#                 log_manager.add_work_log(str(log_msg), sys._getframe().f_code.co_name)

                self.dead_client_dealer(sk_node)
                continue

        for key in self.client_dict.keys():
            self.dead_client_dealer(self.client_dict[key])

        log_msg = '%s Server shutdown! Thread cleaned, remain client number: %d ' %(self.thread_name, len(self.client_list))
        log_handler.work(log_msg)
#         log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)

        print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'

    def dead_client_dealer(self, client):
        """
        删除一个连接实例

        :param client: 待删除的额连接实例
        """
#         try:
#         client.handler.send('***')
#         except socket.error:
        log_msg = "[ %s ] CLOSING DEAD CLIENT %s" %(self.thread_name, str(client.fileno()))
        log_handler.work(log_msg)
#         log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)

#         try:
        client.mylock.acquire()
        self.client_list.remove(client)
        self.client_dict.pop(client.fileno())
#         try:
#             client.handler.shutdown(socket.SHUT_RDWR)
#         except Exception:
#             pass
        client.handler.close()
        client.mylock.release()
#         except Exception, e:
#             print e
#             self.client_list.remove(client)
#             self.client_dict.pop(client.fileno())

if __name__=="__main__":
    temp = SocketList()
    temp.init()
    temp.ram_manage_list()
