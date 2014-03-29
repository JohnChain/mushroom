# !/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from arm_frame_solution import ArmFrameSolution
from task_list import global_task_list, task_condition

class TaskDeliver():
    """
    处理任务队列中的任务，向底层发送任务
    """
    def __init__(self, ):
        pass

    def core(self, stopEvent, param, ):
        """
        :param param: 未用
        :rtype: 0
        """

        log_msg = ' Thread Task Delivery is Ready ...'
        log_handler.work(log_msg)
#         log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)
#         print log_msg

        if task_condition.acquire():
            while not stopEvent.isSet():
                key_list = global_task_list.task_list.keys()
                if  len(key_list) > 0:
                    # TODO: comment or let it go
                    for key in key_list:
#                         log_msg = 'dealing one task'
#                         log_handler.debug(log_msg)
                        try:
                            one_task = global_task_list.task_list[key]
                            if one_task.state == TASK_READY:
                                sender = ArmFrameSolution()
                                sender.send(arm_client_list[1].handler, one_task.frame)
                                one_task.state = TASK_WAITING

                                log_msg = '[ Task Deliver ] Send one task id : %d' %(one_task.id)
                                log_handler.work(log_msg)
#                                 log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)

                            elif one_task.state == TASK_WAITING:
                                now_time = datetime.now()
                                gap = (now_time - one_task.birth_time).seconds
                                if gap > TASK_TIMEOUT:
                                    global_task_list.remove(key)
                            else:
                                global_task_list.remove(key)
                        except NameError, e:
                            log_msg = '[ Task Deliver ] %s' %str(e)
                            continue
                        except IndexError, e:
                            log_msg = '[ Task Deliver ] %s' %str(e)
                            continue
#                 else:
                task_condition.wait(TASK_WAIT_CIRCLE)
#                 log_msg = 'task deliver waked'
#                 log_handler.debug(log_msg)
            task_condition.release()
        else:
            print '!!!!!!!!!!! task_condition not acquired'

        log_msg = '[ Task Deliver ] Task Deliver shutdown and cleaned! '
        log_handler.work(log_msg)
#         log_manager.add_work_log(log_msg, sys._getframe().f_code.co_name)
#         print log_msg
        print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
        exit()
