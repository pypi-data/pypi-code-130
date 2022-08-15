import logging
import time
import typing
from logging.handlers import WatchedFileHandler
from logging import FileHandler
from .handlers import *


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
            self.log_path = Path(home_path) / Path('pythonlogs')
        else:
            self.log_path = '/pythonlogs'
        self.formatter = logging.Formatter('%(asctime)s.%(msecs)03d [%(threadName)s] %(levelname)-8s %(name)s '
                                           '- [%(funcName)s,%(lineno)d] - %(message)s',
                                           "%Y-%m-%d %H:%M:%S")
        self.log_file_backup_count = 3


class LogManager(object):
    """
    日志管理类，用于创建logger和添加handler
    """
    logger_name_list = []
    logger_list = []

    def __init__(self, logger_name: typing.Union[str, None]):
        self._formatter = None
        self._log_file_handler_type = None
        self._log_path = None
        self._log_file_size = None
        self._log_filename = None
        self._is_add_stream_handler = None
        self._do_not_use_color_handler = None
        self._logger_level = None
        self._logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self.log_config = LogConfig()

    def get_logger_and_add_handlers(self):
        self._logger_level = self.log_config.log_level_filter
        self._do_not_use_color_handler = self.log_config.do_not_use_color_handler
        self._is_add_stream_handler = self.log_config.is_add_stream_handler
        self._log_filename = self.log_config.log_filename
        if self._log_filename is None and self.log_config.log_write_to_file:
            self._log_filename = f'{self._logger_name}.log'
        self._log_file_size = self.log_config.log_file_size
        self._log_path = self.log_config.log_path
        self._log_file_handler_type = self.log_config.log_file_handler_type
        self._formatter = self.log_config.formatter
        self.logger.setLevel(self._logger_level)
        self.__add_handlers()
        return self.logger

    def _judge_logger_has_handler_type(self, handler_type: type):
        for hr in self.logger.handlers:
            if isinstance(hr, handler_type):
                return True

    def __add_a_handler(self, handlerx: logging.Handler):
        handlerx.setLevel(10)
        handlerx.setFormatter(self._formatter)
        self.logger.addHandler(handlerx)

    def __add_handlers(self):
        # 添加控制台日志
        # REMIND 添加控制台日志
        if not (self._judge_logger_has_handler_type(ColorHandler) or self._judge_logger_has_handler_type(
                logging.StreamHandler)) and self._is_add_stream_handler:
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
        ) and all([self._log_path, self._log_filename]):
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

    def builder(self, log_level_int: int = None, is_add_stream_handler=True,
                log_write_to_file=False, do_not_use_color_handler=False, log_path=None,
                log_filename=None, log_file_size: int = None, log_file_handler_type: int = None,
                formatter_template: [logging.Formatter] = None):
        """
          :param log_level_int: 日志输出级别，设置为 1 2 3 4 5，分别对应原生logging.DEBUG(10)，logging.INFO(20)，logging.WARNING(30)，logging.ERROR(40),logging.CRITICAL(50)级别，现在可以直接用10 20 30 40 50了，兼容了。
          :param is_add_stream_handler: 是否打印日志到控制台
          :param log_write_to_file: 是否输出到文件中
          :param do_not_use_color_handler :是否禁止使用color彩色日志
          :param log_path: 设置存放日志的文件夹路径,如果不设置，则取nb_log_config.LOG_PATH，如果配置中也没指定则自动在代码所在磁盘的根目录创建/pythonlogs文件夹，
                 非windwos下要注意账号权限问题(如果python没权限在根目录建/pythonlogs，则需要手动先创建好)
          :param log_filename: 日志的名字，仅当log_path和log_filename都不为None时候才写入到日志文件。
          :param log_file_size :日志大小，单位M，默认100M
          :param log_file_handler_type :这个值可以设置为1 2 3 4 四种值，1为使用多进程安全按日志文件大小切割的文件日志
                 2为多进程安全按天自动切割的文件日志，同一个文件，每天生成一个日志
                 3为不自动切割的单个文件的日志(不切割文件就不会出现所谓进程安不安全的问题)
                 4为 WatchedFileHandler，这个是需要在linux下才能使用，需要借助lograte外力进行日志文件的切割，多进程安全。
                 5 为第三方的concurrent_log_handler.ConcurrentRotatingFileHandler按日志文件大小切割的文件日志，
                   这个是采用了文件锁，多进程安全切割，文件锁在linux上使用fcntl性能还行，win上使用win32con性能非常惨。按大小切割建议不要选第5个个filehandler而是选择第1个。

          :param formatter_template :日志模板，如果为数字，则为nb_log_config.py字典formatter_dict的键对应的模板，
                                   1为formatter_dict的详细模板，2为简要模板,5为最好模板。
                                   如果为logging.Formatter对象，则直接使用用户传入的模板。
          :type log_level_int :int
          :type is_add_stream_handler :bool
          :type log_write_to_file :bool
          :type do_not_use_color_handler :bool
          :type log_path :str
          :type log_filename :str
          :type log_file_size :int
          """
        if log_level_int:
            self.log_config.log_level_filter = log_level_int * 10 if log_level_int < 10 else log_level_int
        if is_add_stream_handler is not None:
            self.log_config.is_add_stream_handler = is_add_stream_handler
        if do_not_use_color_handler is not None:
            self.log_config.do_not_use_color_handler = do_not_use_color_handler
        if log_path:
            self.log_config.log_path = log_path
        if log_write_to_file is not None:
            self.log_config.log_write_to_file = log_write_to_file
        self.log_config.log_filename = log_filename
        if log_file_size:
            self.log_config.log_file_size = log_file_size
        if log_file_handler_type not in (None, 1, 2, 3, 4, 5):
            raise ValueError("log_file_handler_type的值必须设置为 1 2 3 4这四个数字")
        if log_file_handler_type:
            self.log_config.log_file_handler_type = log_file_handler_type
        if formatter_template:
            self.log_config.formatter = formatter_template

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


def plog(name, log_level_int: int = None, is_add_stream_handler=True,
         log_write_to_file=False, do_not_use_color_handler=False, log_path=None,
         log_filename=None, log_file_size: int = None, log_file_handler_type: int = None,
         show_run_time=False):
    """
           :param name: 日志命名空间
           :param log_level_int: 日志输出级别，设置为 1 2 3 4 5，分别对应原生logging.DEBUG(10)，logging.INFO(20)，logging.WARNING(30)，logging.ERROR(40),logging.CRITICAL(50)级别，现在可以直接用10 20 30 40 50了，兼容了。
           :param is_add_stream_handler: 是否打印日志到控制台
           :param log_write_to_file: 是否输出到文件中
           :param do_not_use_color_handler :是否禁止使用color彩色日志
           :param log_path: 设置存放日志的文件夹路径,如果不设置，则取nb_log_config.LOG_PATH，如果配置中也没指定则自动在代码所在磁盘的根目录创建/pythonlogs文件夹，
                  非windwos下要注意账号权限问题(如果python没权限在根目录建/pythonlogs，则需要手动 先创建好)
           :param log_filename: 日志的名字，仅当log_path和log_filename都不为None时候才写入到日志文件。
           :param log_file_size :日志大小，单位M，默认100M
           :param log_file_handler_type :这个值可以设置为1 2 3 4 四种值，1为使用多进程安全按日志文件大小切割的文件日志
                  2为多进程安全按天自动切割的文件日志，同一个文件，每天生成一个日志
                  3为不自动切割的单个文件的日志(不切割文件就不会出现所谓进程安不安全的问题)
                  4为 WatchedFileHandler，这个是需要在linux下才能使用，需要借助lograte外力进行日志文件的切割，多进程安全。
                  5 为第三方的concurrent_log_handler.ConcurrentRotatingFileHandler按日志文件大小切割的文件日志，
                    这个是采用了文件锁，多进程安全切割，文件锁在linux上使用fcntl性能还行，win上使用win32con性能非常惨。按大小切割建议不要选第5个个filehandler而是选择第1个。

           :param show_run_time: 是否展示函数运行时间
           :type name :str
           :type log_level_int :int
           :type is_add_stream_handler :bool
           :type log_write_to_file :bool
           :type do_not_use_color_handler :bool
           :type log_path :str
           :type log_filename :str
           :type log_file_size :int
           :type show_run_time :bool
           """

    def decorator(func):
        formatter_template = logging.Formatter('%(asctime)s.%(msecs)03d [%(threadName)s] %(levelname)-8s %(name)s '
                                               f'- [{func.__name__},%(lineno)d] - %(message)s',
                                               "%Y-%m-%d %H:%M:%S")
        _log_manager = LogManager(name)
        _log_manager.builder(log_level_int, is_add_stream_handler, log_write_to_file, do_not_use_color_handler, log_path,
                             log_filename, log_file_size, log_file_handler_type, formatter_template)
        _logger = _log_manager.get_logger_and_add_handlers()

        def computation_time(*args):
            start_time = time.time()
            func(*args, _logger)
            end_time = time.time()
            run_time = end_time - start_time
            if show_run_time:
                _logger.critical(F'run_time: {"%.3f" % run_time}秒')

        return computation_time

    return decorator


log_manager = LogManager('root')
logger = log_manager.get_logger_and_add_handlers()
