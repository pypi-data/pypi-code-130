import os, sys, time
import zq_file, zq_const

log_save = False
log_print_event = []
def log_print_record(fun):
    ''' 日志记录到文档 '''
    def wrapper(*args, **kwargs):
        if log_save:
            #将打印临时保存
            log_path = zq_const.const_merage_logs_dir('save_logs', time.strftime('%Y-%m-%d'))
            temp_log_path = zq_const.const_merage_logs_dir('tlog.txt')
            sys.stdout = open(temp_log_path, 'w', encoding='utf-8')
            fun(*args, **kwargs)
            sys.stdout.close()
            with open(temp_log_path, 'r', encoding='utf-8')as tmp:
                with open(log_path, 'a+', encoding='utf-8')as fp:
                    #写入日志的格式
                    fp.write('[{}][{}]:{}'.format(time.strftime('%Y-%m-%d %X'), fun.__name__,tmp.read()))
        else:
            fun(*args, **kwargs)
    return wrapper

@log_print_record
def log_print(*args, **kwargs):
    ''' 日志打印 '''
    if log_print_event and len(log_print_event) > 0:
        for print_item in log_print_event:
            if print_item:
                print_item(*args, **kwargs)
            else:
                log_print_remove_event(print_item)
    if len(args) > 0 and ('debug' in args[0] or 'warning' in args[0] or 'error' in args[0]):
        print(*args, **kwargs)
    else:
        print('notag', *args, **kwargs)

def log_debug(*args, **kwargs):
    ''' 一般日志打印 '''
    args = tuple(['[%s]debug: '%time.strftime('%Y-%m-%d %H:%M:%S')] + list(args))
    log_print(*args, **kwargs)
    
def log_warning(*args, **kwargs):
    ''' 警告日志打印 '''
    args = tuple(['[%s]warning: '%time.strftime('%Y-%m-%d %H:%M:%S')] + list(args))
    log_print(*args, **kwargs)
    
def log_error(*args, **kwargs):
    ''' 错误日志打印 '''
    args = tuple(['[%s]error: '%time.strftime('%Y-%m-%d %H:%M:%S')] + list(args))
    log_print(*args, **kwargs)
    

def log_print_append_event(fun):
    ''' 注册日志相应事件 '''
    log_print_event.append(fun)

def log_print_remove_event(fun):
    ''' 销毁日志相应事件 '''
    log_print_event.remove(fun)

def log_progress_bar(portion, total, desc = ''):
    '''
    打印进度条
    :param portion: 已经接收的数据量
    :param total: 总数据量
    :return: 接收数据完成，返回True
    '''
    part = total / 50  # 1%数据的大小
    count = int(portion / part)
    sys.stdout.write('\r')
    sys.stdout.write('debug: %s'%desc+('[%-50s]%.2f%%' % (('>' * count), portion / total * 100)))
    sys.stdout.flush()

    if portion >= total:
        sys.stdout.write('\n')
        return True
    return False

def log_take_up_time(fun):
    ''' 日志记录耗时 '''
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fun(*args, **kwargs)
        end = time.time()
        log_debug('运行耗时 %s : %s'%(fun.__qualname__, end-start))
        return result
    return wrapper