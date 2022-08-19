import logging
from logging import Logger, RootLogger, Manager, getLogger
import threading
import time
import typing
from . import monkey_patch
from logging.handlers import WatchedFileHandler
from logging import FileHandler
from logging import Logger, PlaceHolder
from .handlers import *
# from log_manager import LogManager

_lock = threading.RLock()

def _acquireLock():
    """
    Acquire the module-level lock for serializing access to shared data.

    This should be released with _releaseLock().
    """
    if _lock:
        _lock.acquire()


def _releaseLock():
    """
    Release the module-level lock acquired by calling _acquireLock().
    """
    if _lock:
        _lock.release()

CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0


class MyLogger(Logger):
    """
    继承logging 的 Logger,加入plog方法
    """
    def __init__(self, name, level=NOTSET):

        super().__init__(name, level)
        self._cache = {}

    def plog(self, name: typing.Optional[str] = 'plog', log_level_int: int = None, is_add_stream_handler: bool = True,
             log_write_to_file: bool = False, do_not_use_color_handler: bool = False, log_file_path: str = None,
             log_filename: str = None, log_file_size: int = None, log_file_handler_type: int = None,
             show_run_time: bool = False, log_switch: bool = True):
        """
               :param name: 日志命名空间
               :param log_level_int: 日志输出级别，设置为 1 2 3 4 5，分别对应原生logging.DEBUG(10)，logging.INFO(20)，logging.WARNING(30)，logging.ERROR(40),logging.CRITICAL(50)级别，现在可以直接用10 20 30 40 50了，兼容了。
               :param is_add_stream_handler: 是否打印日志到控制台
               :param log_write_to_file: 是否输出到文件中
               :param do_not_use_color_handler :是否禁止使用color彩色日志
               :param log_file_path: 设置存放日志的文件夹路径,如果不设置，默认在代码所在磁盘的根目录创建/pythonlogs文件
               :param log_filename: 日志的名字，当log_write_to_file为True时才写入日志。
               :param log_file_size :日志大小，单位M，默认100M
               :param log_file_handler_type :这个值可以设置为1 2 3 4 四种值，1为使用多进程安全按日志文件大小切割的文件日志
                      2为多进程安全按天自动切割的文件日志，同一个文件，每天生成一个日志
                      3为不自动切割的单个文件的日志(不切割文件就不会出现所谓进程安不安全的问题)
                      4为 WatchedFileHandler，这个是需要在linux下才能使用，需要借助lograte外力进行日志文件的切割，多进程安全。
                      5 为第三方的concurrent_log_handler.ConcurrentRotatingFileHandler按日志文件大小切割的文件日志，
                        这个是采用了文件锁，多进程安全切割，文件锁在linux上使用fcntl性能还行，win上使用win32con性能非常惨。按大小切割建议不要选第5个个filehandler而是选择第1个。

               :param show_run_time: 是否展示函数运行时间
               :param log_switch: 日志开关，是否开启日志， True：开启  False: 关闭
               :type name :str
               :type log_level_int :int
               :type is_add_stream_handler :bool
               :type log_write_to_file :bool
               :type do_not_use_color_handler :bool
               :type log_file_path :str
               :type log_filename :str
               :type log_file_size :int
               :type show_run_time :bool
               :type log_switch :bool
               """

        def decorator(func):
            formatter_template = logging.Formatter('%(asctime)s.%(msecs)03d [%(threadName)s] %(levelname)-8s %(name)s '
                                                   f'- [{func.__name__},%(lineno)d] - %(message)s',
                                                   "%Y-%m-%d %H:%M:%S")
            _log_manager = LogManager(name)
            _logger = _log_manager.get_builder().set_log_switch(log_switch)\
                                                .set_log_level_int(log_level_int)\
                                                .set_is_add_stream_handler(is_add_stream_handler)\
                                                .set_log_write_to_file(log_write_to_file)\
                                                .set_do_not_use_color_handler(do_not_use_color_handler)\
                                                .set_log_file_path(log_file_path).set_log_filename(log_filename)\
                                                .set_log_file_size(log_file_size).set_log_file_handler_type(log_file_handler_type)\
                                                .set_formatter_template(formatter_template).builder()

            def computation_time(*args):
                start_time = time.time()
                func(*args, _logger)
                end_time = time.time()
                run_time = end_time - start_time
                if show_run_time:
                    _logger.critical(F'run_time: {"%.3f" % run_time}秒')

            return computation_time

        return decorator


class MyRootLogger(MyLogger):
    def __init__(self, level):
        """
        Initialize the logger with the name "root".
        """
        MyLogger.__init__(self, "root", level)

    def __reduce__(self):
        return get_logger, ()


class MyManager(object):
    """
    There is [under normal circumstances] just one Manager instance, which
    holds the hierarchy of loggers.
    """
    def __init__(self, rootnode):
        """
        Initialize the manager with the root node of the logger hierarchy.
        """
        self.root = rootnode
        self.disable = 0
        self.emittedNoHandlerWarning = False
        self.loggerDict = {}
        self.loggerClass = None
        self.logRecordFactory = None

    def getLogger(self, name):
        """
        Get a logger with the specified name (channel name), creating it
        if it doesn't yet exist. This name is a dot-separated hierarchical
        name, such as "a", "a.b", "a.b.c" or similar.

        If a PlaceHolder existed for the specified name [i.e. the logger
        didn't exist but a child of it did], replace it with the created
        logger and fix up the parent/child references which pointed to the
        placeholder to now point to the logger.
        """
        rv = None
        if not isinstance(name, str):
            raise TypeError('A logger name must be a string')
        _acquireLock()
        try:
            if name in self.loggerDict:
                rv = self.loggerDict[name]
                if isinstance(rv, PlaceHolder):
                    ph = rv
                    rv = (self.loggerClass or _loggerClass)(name)
                    rv.manager = self
                    self.loggerDict[name] = rv
                    self._fixupChildren(ph, rv)
                    self._fixupParents(rv)
            else:
                rv = (self.loggerClass or _loggerClass)(name)
                rv.manager = self
                self.loggerDict[name] = rv
                self._fixupParents(rv)
        finally:
            _releaseLock()
        return rv

    def setLoggerClass(self, klass):
        """
        Set the class to be used when instantiating a logger with this Manager.
        """
        if klass != MyLogger:
            if not issubclass(klass, MyLogger):
                raise TypeError("logger not derived from logging.Logger: "
                                + klass.__name__)
        self.loggerClass = klass

    def setLogRecordFactory(self, factory):
        """
        Set the factory to be used when instantiating a log record with this
        Manager.
        """
        self.logRecordFactory = factory

    def _fixupParents(self, alogger):
        """
        Ensure that there are either loggers or placeholders all the way
        from the specified logger to the root of the logger hierarchy.
        """
        name = alogger.name
        i = name.rfind(".")
        rv = None
        while (i > 0) and not rv:
            substr = name[:i]
            if substr not in self.loggerDict:
                self.loggerDict[substr] = PlaceHolder(alogger)
            else:
                obj = self.loggerDict[substr]
                if isinstance(obj, MyLogger):
                    rv = obj
                else:
                    assert isinstance(obj, PlaceHolder)
                    obj.append(alogger)
            i = name.rfind(".", 0, i - 1)
        if not rv:
            rv = self.root
        alogger.parent = rv

    def _fixupChildren(self, ph, alogger):
        """
        Ensure that children of the placeholder ph are connected to the
        specified logger.
        """
        name = alogger.name
        namelen = len(name)
        for c in ph.loggerMap.keys():
            #The if means ... if not c.parent.name.startswith(nm)
            if c.parent.name[:namelen] != name:
                alogger.parent = c.parent
                c.parent = alogger

    def _clear_cache(self):
        """
        Clear the cache for all loggers in loggerDict
        Called when level changes are made
        """

        _acquireLock()
        for logger in self.loggerDict.values():
            if isinstance(logger, MyLogger):
                logger._cache.clear()
        self.root._cache.clear()
        _releaseLock()


root = MyRootLogger(30)
MyLogger.root = root
MyLogger.manager = MyManager(MyLogger.root)
_loggerClass = MyLogger


def get_logger(name):
    if name:
        return MyLogger.manager.getLogger(name)
    else:
        return root


class LogConfig:
    """
    日志配置
    """

    def __init__(self):
        self.log_level_filter = logging.DEBUG
        self.log_write_to_file = False
        self.is_add_stream_handler = True
        self.do_not_use_color_handler = False
        self.log_filename = None
        self.log_file_size = 100
        self.log_file_handler_type = 1  # 1,2,3,4,5
        if os.name == 'posix':
            home_path = os.environ.get("HOME", '/')  # 这个是获取linux系统的当前用户的主目录，不需要亲自设置
            self.log_file_path = Path(home_path) / Path('pythonlogs')
        else:
            self.log_file_path = '/pythonlogs'
        self.formatter = logging.Formatter('%(asctime)s.%(msecs)03d [%(threadName)s] %(levelname)-8s %(name)s '
                                           '- [%(funcName)s,%(lineno)d] - %(message)s',
                                           "%Y-%m-%d %H:%M:%S")
        self.log_file_backup_count = 3
        self.log_switch = True    # 日志开关 True: 开  False: 关

class LogManager(object):
    """
    日志管理类，用于创建logger和添加handler
    """
    logger_name_list = []
    logger_list = []
    _instance_lock = threading.Lock()

    def __init__(self, logger_name: typing.Optional[str] = 'plog'):
        self._formatter = None
        self._log_file_handler_type = None
        self._log_path = None
        self._log_file_size = None
        self._log_filename = None
        self._is_add_stream_handler = None
        self._do_not_use_color_handler = None
        self._logger_level = None
        self._log_switch = None
        self._logger_name = logger_name
        self.logger = get_logger(logger_name)
        self.log_config = LogConfig()

    def get_logger_and_add_handlers(self):
        self._logger_level = self.log_config.log_level_filter
        self._do_not_use_color_handler = self.log_config.do_not_use_color_handler
        self._is_add_stream_handler = self.log_config.is_add_stream_handler
        if self.log_config.log_write_to_file:
            # 只有要写入文件的开关  开着 才能写入
            self._log_filename = self.log_config.log_filename
        if self._log_filename is None and self.log_config.log_write_to_file:
            # 如果写入文件的开关开着， 并且没有指定日志文件的名字时
            self._log_filename = f'{self._logger_name}.log'
        self._log_file_size = self.log_config.log_file_size
        self._log_path = self.log_config.log_file_path
        self._log_file_handler_type = self.log_config.log_file_handler_type
        self._formatter = self.log_config.formatter
        self._log_switch = self.log_config.log_switch
        self.logger.setLevel(self._logger_level)
        self.__add_handlers()
        return self.logger

    def _judge_logger_has_handler_type(self, handler_type: type):
        for hr in self.logger.handlers:
            if isinstance(hr, handler_type):
                return True
        return False

    def __add_a_handler(self, handlerx: logging.Handler):
        handlerx.setLevel(10)
        handlerx.setFormatter(self._formatter)
        self.logger.addHandler(handlerx)

    def __cycle_remove_handlers(self):
        for hr in self.logger.handlers:
            self.logger.removeHandler(hr)

    def __add_handlers(self):
        self.__cycle_remove_handlers()
        # 添加控制台日志
        # REMIND 添加控制台日志
        if not (self._judge_logger_has_handler_type(ColorHandler) or self._judge_logger_has_handler_type(
                logging.StreamHandler)) and self._is_add_stream_handler and self._log_switch:
            handler = ColorHandler() if not self._do_not_use_color_handler else logging.StreamHandler()  # 不使用streamhandler，使用自定义的彩色日志
            # handler = logging.StreamHandler()
            handler.setLevel(self._logger_level)
            self.__add_a_handler(handler)

        # REMIND 添加多进程安全切片的文件日志
        if not (self._judge_logger_has_handler_type(ConcurrentRotatingFileHandler) or
                self._judge_logger_has_handler_type(ConcurrentRotatingFileHandlerWithBufferInitiativeWindwos) or
                self._judge_logger_has_handler_type(ConcurrentRotatingFileHandlerWithBufferInitiativeLinux) or
                self._judge_logger_has_handler_type(ConcurrentDayRotatingFileHandler) or
                self._judge_logger_has_handler_type(FileHandler) or
                self._judge_logger_has_handler_type(ConcurrentRotatingFileHandler)
        ) and all([self._log_path, self._log_filename]) and self._log_switch:
            if not os.path.exists(self._log_path):
                os.makedirs(self._log_path)
            log_file = os.path.join(self._log_path, self._log_filename)
            file_handler = None
            if self._log_file_handler_type == 1:
                if os_name == 'nt':
                    # 在win下使用这个ConcurrentRotatingFileHandler可以解决多进程安全切片，但性能损失惨重。
                    # 10进程各自写入10万条记录到同一个文件消耗15分钟。比不切片写入速度降低100倍。
                    file_handler = ConcurrentRotatingFileHandlerWithBufferInitiativeWindwos(log_file,
                                                                                            maxBytes=self._log_file_size * 1024 * 1024,
                                                                                            backupCount=self.log_config.log_file_backup_count,
                                                                                            encoding="utf-8")
                elif os_name == 'posix':
                    # linux下可以使用ConcurrentRotatingFileHandler，进程安全的日志方式。
                    # 10进程各自写入10万条记录到同一个文件消耗100秒，还是比不切片写入速度降低10倍。因为每次检查切片大小和文件锁的原因。
                    file_handler = ConcurrentRotatingFileHandlerWithBufferInitiativeLinux(log_file,
                                                                                          maxBytes=self._log_file_size * 1024 * 1024,
                                                                                          backupCount=self.log_config.log_file_backup_count,
                                                                                          encoding="utf-8")

            elif self._log_file_handler_type == 4:
                file_handler = WatchedFileHandler(log_file)
            elif self._log_file_handler_type == 2:
                file_handler = ConcurrentDayRotatingFileHandler(self._log_filename, self._log_path,
                                                                back_count=self.log_config.log_file_backup_count, )
            elif self._log_file_handler_type == 3:
                file_handler = FileHandler(log_file, mode='a', encoding='utf-8')
            elif self._log_file_handler_type == 5:
                file_handler = ConcurrentRotatingFileHandler(log_file,
                                                             maxBytes=self._log_file_size * 1024 * 1024,
                                                             backupCount=self.log_config.log_file_backup_count,
                                                             encoding="utf-8")
            file_handler.setLevel(self._logger_level)
            self.__add_a_handler(file_handler)

    def remove_all_handlers(self):
        self.logger.handlers = []

    def remove_handler_by_handler_class(self, handler_class: type):
        """
        去掉指定类型的handler
        :param handler_class:logging.StreamHandler,ColorHandler,MongoHandler,ConcurrentRotatingFileHandler,MongoHandler,CompatibleSMTPSSLHandler的一种
        :return:
        """
        if handler_class not in (
                logging.StreamHandler, ColorHandler, ConcurrentRotatingFileHandler):
            raise TypeError('设置的handler类型不正确')
        all_handlers = copy.copy(self.logger.handlers)
        for handler in all_handlers:
            if isinstance(handler, handler_class):
                self.logger.removeHandler(handler)  # noqa

    def get_builder(self):

        class Builder(object):
            def __init__(self, log_manage: LogManager):
                self.obj = log_manage

            def set_log_switch(self, log_switch: bool):
                """
                设置日志开关
                """
                self.obj.log_config.log_switch = log_switch
                return self

            def set_log_level_int(self, log_level):
                """
                设置日志输出级别, 级别从低到高为 debug, info, warning, error, critical
                :param log_level: 日志级别
                :return: 返回builder对象
                """
                if log_level is None:
                    self.obj.log_config.log_level_filter = self.obj.log_config.log_level_filter
                else:
                    self.obj.log_config.log_level_filter = log_level
                return self

            def set_is_add_stream_handler(self, is_add_stream_handler: bool):
                """
                设置日志是否输出到控制台。True:是, False:否，默认为True
                """
                self.obj.log_config.is_add_stream_handler = is_add_stream_handler
                return self

            def set_log_write_to_file(self, log_write_to_file: bool):
                """
                设置日志是否输出到文件  True:是, False:否 默认为False
                """
                self.obj.log_config.log_write_to_file = log_write_to_file
                return self

            def set_do_not_use_color_handler(self, do_not_use_color_handler: bool):
                """
                设置是否禁止使用color彩色日志  True:禁用, False:否不禁用  默认为False
                """
                self.obj.log_config.do_not_use_color_handler = do_not_use_color_handler
                return self

            def set_log_file_path(self, log_file_path: str):
                """
                设置存放日志的文件夹路径, 默认为 pythonlogs 文件夹
                """
                if log_file_path is None:
                    self.obj.log_config.log_file_path = self.obj.log_config.log_file_path
                else:
                    self.obj.log_config.log_file_path = log_file_path
                return self

            def set_log_filename(self, log_filename: str):
                """
                设置日志输出到文件夹中的名字， 如果要输出到文件中， 默认为命名空间的名字
                """
                self.obj.log_config.log_filename = log_filename
                return self

            def set_log_file_size(self, log_file_size: int):
                """
                设置日志大小，单位M，默认100M
                """
                if log_file_size is None:
                    self.obj.log_config.log_file_size = self.obj.log_config.log_file_size
                else:
                    self.obj.log_config.log_file_size = log_file_size
                return self

            def set_log_file_handler_type(self, log_file_handler_type: int):
                """
                设置日志采取哪种方式写入到文件，默认为第一种
                :param log_file_handler_type:
                这个值可以设置为1 2 3 4 四种值，
                    1.为使用多进程安全按日志文件大小切割的文件日志
                    2.为多进程安全按天自动切割的文件日志，同一个文件，每天生成一个日志
                    3.为不自动切割的单个文件的日志(不切割文件就不会出现所谓进程安不安全的问题)
                    4.为 WatchedFileHandler，这个是需要在linux下才能使用，需要借助lograte外力进行日志文件的切割，多进程安全。
                    5.为第三方的concurrent_log_handler.ConcurrentRotatingFileHandler按日志文件大小切割的文件日志，
                这个是采用了文件锁，多进程安全切割，文件锁在linux上使用fcntl性能还行，win上使用win32con性能非常惨。按大小切割建议不要选第5个个filehandler而是选择第1个。
                """
                if log_file_handler_type is None:
                    self.obj.log_config.log_file_handler_type = self.obj.log_config.log_file_handler_type
                else:
                    self.obj.log_config.log_file_handler_type = log_file_handler_type
                return self

            def set_formatter_template(self, formatter_template):
                """
                设置日志的输出模板
                """
                self.obj.log_config.formatter = formatter_template
                return self

            def builder(self):
                """
                创建logger对象
                """
                _logger = self.obj.get_logger_and_add_handlers()
                return _logger
        return Builder(self)


log_manager = LogManager()
logger = log_manager.get_builder().builder()