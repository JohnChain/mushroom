# -*- coding:utf-8 -*-
# from head import log_conf
from head import *
# from utils import *

class LogType:
    """
    日志类
    """
    #: 记录时间
    time = ''
    #: 日志类型
    type = ''
    #: 日志信息
    msg  = ''
    #: 日志产生位置
    location = ''

class LogManager:
    """
    日志管理模块,包括写入日志,待写日志队列的维护等功能,初始化时创建独立线程负责从待写日志队列中取出日志，写入相应文件
    """

    def __init__(self, ):
        #: 日志实例队列
        self.record_list = []

    def log_configure(self, log_error = 1, log_communication = 1, log_debug = 1, log_work = 1):
        """
        配置日志记录类型

        :param log_error: 错误日志（0/1）
        :param log_communication: 通信日志（0/1）
        :param log_debug: 调试日志（0/1）
        :param log_work: 工作日志（0/1）
        :rtype:
        """
        log_conf["ERROR"]           = log_error
        log_conf["COMMUNICATION"]   = log_communication
        log_conf["DEBUG"]           = log_debug
        log_conf["WORK"]            = log_work

    def writer_record(self, one_record):
        """
        写入日志文件函数

        :param one_record: 向相应日志文件一条日志
        :rtype: 0 if succeed, -1 if failed
        """
        fd = open(log_file[one_record.type], 'a+')
        fd.write(one_record.type)
        fd.write('\t || \t')
        fd.write(one_record.time)
        fd.write('\t || \t')
        fd.write(one_record.msg)
        fd.write('\t || \t')
        fd.write(one_record.location)
        fd.write('\n')
        fd.close()

    def view_record(self, type):
        """
        查看日志

        :param type: 查看的日志类型
        :rtype: 待定
        """
        list_len = len(self.record_list)
        if type == 'error':
            for i in range(list_len):
                if self.record_list[i].type == 'ERROR':
                    return self.record_list[i]
        elif type == 'working':
            for i in range(list_len):
                if self.record_list[i].type == 'WORKING':
                    return self.record_list[i]

        elif type == 'communication':
            for i in range(list_len):
                if self.record_list[i].type == 'COMMUNICATION':
                    return self.record_list[i]
        elif type == 'debug':
            for i in range(list_len):
                if self.record_list[i].type == 'DEBUG':
                    return self.record_list[i]
        else:
            return ''

    def add_record(self, log_type, log_msg, location = sys._getframe().f_code.co_name):
        """
        向日志队列追加一条日志

        :param log_type: 日志类型， 分类见 head文件中的 log_conf 字典
        :param log_msg: 日志信息
        :rtype: 0 if succeed, -1 if failed
        """
        if log_conf[log_type] == 1:
            log_instance = LogType()
            log_instance.time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_instance.type = log_type
            log_instance.msg  = log_msg
            log_instance.location = location
            self.record_list.append(log_instance)

    def add_error_log(self, log_msg, location = sys._getframe().f_code.co_name):
        """
        向日志队列追加一条日志

        :param log_msg: 日志信息
        :rtype: 0 if succeed, -1 if failed
        """
        if log_conf['ERROR'] == 1:
            log_instance = LogType()
            log_instance.time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_instance.type = 'ERROR'
            log_instance.msg  = log_msg
            log_instance.location = location
            self.record_list.append(log_instance)

    def add_communication_log(self, log_msg, location = sys._getframe().f_code.co_name):
        """
        向日志队列追加一条日志

        :param log_msg: 日志信息
        :rtype: 0 if succeed, -1 if failed
        """
        if log_conf['COMMUNICATION'] == 1:
            log_instance = LogType()
            log_instance.time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_instance.type = 'COMMUNICATION'
            log_instance.msg  = log_msg
            log_instance.location = location
            self.record_list.append(log_instance)

    def add_work_log(self, log_msg, location = sys._getframe().f_code.co_name):
        """
        向日志队列追加一条日志

        :param log_msg: 日志信息
        :rtype: 0 if succeed, -1 if failed
        """
        if log_conf['WORK'] == 1:
            log_instance = LogType()
            log_instance.time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_instance.type = 'WORK'
            log_instance.msg  = log_msg
            log_instance.location = location
            self.record_list.append(log_instance)

    def add_debug_log(self, log_msg, location = sys._getframe().f_code.co_name):
        """
        向日志队列追加一条日志

        :param log_msg: 日志信息
        :rtype: 0 if succeed, -1 if failed
        """
        if log_conf['DEBUG'] == 1:
            log_instance = LogType()
            log_instance.time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_instance.type = 'DEBUG'
            log_instance.msg  = log_msg
            log_instance.location = location
            self.record_list.append(log_instance)

    def remove_one_record(self, ):
        """
        从日志队列删除一条日志

        :param one_record: 从日志队列删除一条日志
        :rtype: 一条日志对象 if succeed, NULL if failed
        """
        try:
            result = self.record_list.pop(0)
        except IndexError:
            result = ''
        finally:
            return result

    def record_thread_main(self, stopEvent, param = '' ):
        """
        日志线程主函数

        :param param: 未用
        :rtype: None
        """
        log_msg = 'Log Manager Thread Ready'
        self.add_work_log(log_msg, sys._getframe().f_code.co_name)

        def timer_work():
            length = len(self.record_list)
            for i in range(length):
                log_instance = self.remove_one_record()
                if log_instance != '':
                    if log_conf[log_instance.type] == 1:
                        self.writer_record(log_instance)
                else:
                    print "empyt log list"
                    break

        timer = Timer(LOG_TIMER_CYCLE, timer_work)
        timer.start()
        while not stopEvent.isSet():
            if not timer.is_alive():
                timer = Timer(LOG_TIMER_CYCLE, timer_work)
                timer.start()
            else:
                sleep(0.1)
        if timer.is_alive():
            timer.join()
        log_msg = 'Log Manager Thread closed and cleaned'
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> "
    def record_thread_close(self, ):
        """
        关闭日志线程

        :rtype: 0 if succeed, -1 if failed
        """
        pass


FOREGROUND_WHITE = 0x0007
FOREGROUND_BLUE = 0x01 # text color contains blue.
FOREGROUND_GREEN= 0x02 # text color contains green.
FOREGROUND_RED  = 0x04 # text color contains red.
FOREGROUND_YELLOW = FOREGROUND_RED | FOREGROUND_GREEN

STD_OUTPUT_HANDLE= -11
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

def set_color(color, handle=std_out_handle):
    bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return bool

class Logger():
    def __init__(self, param, \
                 work_path = log_file['WORK'], \
                 communication_path = log_file['COMMUNICATION'], \
                 debug_path = log_file['DEBUG'], 
                 error_path = log_file['ERROR']):
        self.work_log = logging.getLogger('WORK')
        self.work_log.setLevel(logging.DEBUG)
        self.communication_log = logging.getLogger('COMMUNICATION')
        self.communication_log.setLevel(logging.DEBUG)
        self.error_log = logging.getLogger('ERROR')
        self.error_log.setLevel(logging.DEBUG)
        self.debug_log = logging.getLogger('DEBUG')
        self.debug_log.setLevel(logging.DEBUG)
        
        fmt = logging.Formatter('[%(asctime)s] [Level = %(levelname)s] [ThreadName = %(threadName)s] [ThreadID = %(thread)d] -- %(message)s', '%Y-%m-%d %H:%M%S')

        #设置CMD日志
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(logging.DEBUG)
        
        #设置文件日志
        work_fh = logging.FileHandler(work_path)
        work_fh.setFormatter(fmt)
        work_fh.setLevel(logging.INFO)

        communication_fh = logging.FileHandler(communication_path)
        communication_fh.setFormatter(fmt)
        communication_fh.setLevel(logging.INFO)

        error_fh = logging.FileHandler(error_path)
        error_fh.setFormatter(fmt)
        error_fh.setLevel(logging.ERROR)

        debug_fh = logging.FileHandler(debug_path)
        debug_fh.setFormatter(fmt)
        debug_fh.setLevel(logging.DEBUG)

        self.work_log.addHandler(sh)
        self.communication_log.addHandler(sh)
        self.error_log.addHandler(sh)
        self.debug_log.addHandler(sh)
  
        self.work_log.addHandler(work_fh)
        self.communication_log.addHandler(communication_fh)
        self.error_log.addHandler(error_fh)
        self.debug_log.addHandler(debug_fh)

    def debug(self, msg):
        self.debug_log.debug(msg)

    def work(self, msg):
        self.work_log.info(msg)

#     def communication(self,msg,):
#         self.communication_log.info(msg)
# 
#     def error(self, msg):
#         self.error_log.error(msg)

    def communication(self,msg, color = FOREGROUND_YELLOW):
        set_color(color)
        self.communication_log.info(msg)
        set_color(FOREGROUND_WHITE)
 
    def error(self, msg, color=FOREGROUND_RED):
        set_color(color)
        self.error_log.error(msg)
        set_color(FOREGROUND_WHITE)

    def enable_work(self):
        self.work_log.setLevel(logging.INFO)
    def disable_work(self):
        self.work_log.setLevel(logging.WARNING)
    
    def enable_communication(self):
        self.communication_log.setLevel(logging.INFO)
    def disable_communication(self):
        self.communication_log.setLevel(logging.WARNING)
    
    def enable_debug(self):
        self.debug_log.setLevel(logging.DEBUG)
    def disable_debug(self):
        self.debug_log.setLevel(logging.INFO)
    
    def enable_error(self):
        self.error_log.setLevel(logging.ERROR)
    def disable_error(self):
        self.error_log.setLevel(logging.CRITICAL)

if __name__ == '__main__':

    def inser(name):
        while True:
            error_type = 'ERROR'
            error_msg = name + 'error'
            communication_type = 'COMMUNICATION'
            communication_msg = name + 'communication'
            debug_type = 'DEBUG'
            debug_msg = name + 'debug'
            work_type = 'WORK'
            work_msg = name + 'work'
            location = sys._getframe().f_code.co_name
            print "======== in %s======" %name

            temp.add_record(error_type, error_msg, location)
            temp.add_record(communication_type, communication_msg, location)
            temp.add_record(debug_type, debug_msg, location)
            temp.add_record(work_type, work_msg, location)
            sleep(1)

    temp = LogManager()
#     temp.log_configure(1, 0, 0, 0)
#     temp.log_configure(0, 1, 0, 0)
#     temp.log_configure(0, 0, 1, 0)
    temp.log_configure(1, 1, 1, 1)

    log_thread = threading.Thread(target = temp.record_thread_main)
    log_thread.start()

    log_thread = threading.Thread(target = inser, args = ('first', ))
    log_thread.start()

    log_thread = threading.Thread(target = inser, args = ('second', ))
    log_thread.start()

    print "in main_thread"
