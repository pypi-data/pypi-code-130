# -*- coding: UTF-8 -*-

import inspect
import ctypes
import threading
import multiprocessing
import types
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
import asyncio
import time
import traceback
from multiprocessing import Manager
import importlib

'''需要在if __name__=='__main__':的环境下运行'''


# 获取cpu数量
def getCPUNumber():
    return multiprocessing.cpu_count()


# # 获取进程同步对象
# def getManager():
#     # 需要在if __name__=="__main__"下执行
#     return multiprocessing.Manager()


# 不好用，进程出错不会通知
# 进程池
def processPool(maxnum, func, argslist, onevalue=False):
    pool = ProcessPoolExecutor(max_workers=maxnum)
    ps = []
    for args in argslist:
        if onevalue:
            ps.append(pool.submit(func, args))  # 放入单值
        else:
            ps.append(pool.submit(func, *args))  # 执行多值
    # pools.map(func, *argslist)  # 维持执行的进程总数为num，当一个进程执行完毕后会开始执行排在后面的进程
    return pool, ps


# 不好用，线程出错不会通知
# 线程池
def threadPool(maxnum, func, argslist, onevalue=False):
    pool = ThreadPoolExecutor(max_workers=maxnum)
    ps = []
    for args in argslist:
        if onevalue:
            ps.append(pool.submit(func, args))  # 放入单值
        else:
            ps.append(pool.submit(func, *args))  # 执行多值
    # pools.map(func, *argslist)  # 维持执行的进程总数为num，当一个进程执行完毕后会开始执行排在后面的进程
    return pool, ps


# 获取进程同步管理对象
def getProcessManager():
    return Manager()


# 多进程
# 参数不能是自定义类型的实例对象，或者这种实例对象的方法
def process_run(func, argslist: list, ifwait=True):
    ns = []
    for args in argslist:
        n = multiprocessing.Process(target=func, args=tuple(args))
        ns.append(n)
    [n.start() for n in ns]
    if ifwait: [n.join() for n in ns]


# 多线程
def threads_run(func, argslist: list, ifone=False, ifwait=True):
    ns = []
    for args in argslist:
        if ifone: args = (args,)
        n = threading.Thread(target=func, args=tuple(args))
        n.setDaemon(True)  # 设置为守护线程
        ns.append(n)
    [n.start() for n in ns]
    if ifwait: [n.join() for n in ns]


def thread_auto_run(arg_func, args, threadnum: int, ifwait=True):
    lock = threading.Lock()
    args = list(args)
    length = len(args)

    def temp():
        while True:
            lock.acquire()
            if len(args) > 0:
                arg = args.pop(0)
                print(f'\r{length - len(args)}/{length}', end='')
            else:
                lock.release()
                break
            lock.release()
            try:
                arg_func(arg)
            except:
                traceback.print_exc()
                lock.acquire()
                args.append(arg)
                print(f'\r{length - len(args)}/{length}', end='')
                lock.release()

    ts = [threading.Thread(target=temp) for i in range(threadnum)]
    [t.start() for t in ts]
    if ifwait: [t.join() for t in ts]


# 获取当前子线程的id
def getThreadId():
    return threading.currentThread().ident


# 协程运行
def tasksRun(*tasks):
    # 返回为list,序列对应协程序列
    if len(tasks) == 1:
        return asyncio.get_event_loop().run_until_complete(asyncio.gather(tasks[0]))
    else:
        return asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))


##仅用于旧版代码,不建议使用
def retryFunc(func):
    def temp(*values, **kwargs):
        index = kwargs.get('index', '')
        ci = kwargs.get('ci', 3)
        sleeptime = kwargs.get('sleeptime', 5)
        sleepfunc = kwargs.get('sleepfunc', time.sleep)
        iftz = kwargs.get('iftz', True)
        iftz = True
        for i in range(1, ci + 1):
            try:
                return func(*values, **kwargs)
            except:
                if iftz:
                    traceback.print_exc()
                    print(index, '失败，正在重试...第', i, '次，休息', sleeptime, '秒')
                if sleeptime > 0: sleepfunc(sleeptime)
        print('错误参数组：', values)
        assert False, '重试全部失败，抛出错误'

    return temp


# 需设置参数
def retryFunc_args(name='', ci=3, sleeptime=5, sleepfunc=time.sleep, iftz=True):
    def retryFunc(func):
        def temp(*values, **kwargs):
            for i in range(1, ci + 1):
                try:
                    return func(*values, **kwargs)
                except:
                    if iftz:
                        traceback.print_exc()
                        print(name, '失败，正在重试...第', i, '次，休息', sleeptime, '秒')
                    if sleeptime > 0: sleepfunc(sleeptime)
            print('错误参数组：', values)
            assert False, '重试全部失败，抛出错误'

        return temp

    return retryFunc


# 多任务分配
def getTasks(num, taskdatas):
    tasklen = len(taskdatas)
    if tasklen == 0: return []
    num = min(num, tasklen)
    cellnum = tasklen // num if tasklen % num == 0 else tasklen // num + 1
    tasks = list()
    for i in range(0, tasklen, cellnum):
        tasks.append(taskdatas[i:i + cellnum])
    return tasks


# 重新加载当前导入的所有模块
def reloadAllModel():
    print(dir())
    for model in dir():
        if '__' not in model:
            print(model)
            print(types.ModuleType(model))
            importlib.reload(model)


# 会使打包功能出问题
# # 超时机制装饰器
# def timeoutRaiseFunc(timeout, ifraise=True):
#     def temp0(func):
#         def temp(*args, **kwargs):
#             eventlet.monkey_patch()  # 必须加这条代码
#             with eventlet.Timeout(timeout, False):  # 设置超时时间为2秒
#                 return func(*args, **kwargs)
#             if ifraise:
#                 raise TimeoutError()
#             else:
#                 return None
#
#         return temp
#
#     return temp0


# 自定义线程类模型
class Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.__alive = False

    def start(self):
        threading.Thread.start(self)
        self.__alive = True

    def stop(self):
        self.__alive = False
        stopThread(self)

    def is_alive(self):
        return threading.Thread.is_alive(self) and self.__alive


# 关闭线程
def stopThread(thread):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(thread.ident)
    if not inspect.isclass(SystemExit):
        exctype = type(SystemExit)
    else:
        exctype = SystemExit
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
