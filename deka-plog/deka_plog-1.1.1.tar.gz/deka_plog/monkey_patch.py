import logging

from .handlers import *


def revision_call_handlers(self, record):  # 对logging标准模块打猴子补丁。主要是使父命名空间的handler不重复记录当前命名空间日志已有种类的handler。
    """
    import logging

    logger1 = logging.getLogger('a')
    logger1.addHandler(logging.StreamHandler())

    logger2 = logging.getLogger('a.b')
    logger2.addHandler(logging.StreamHandler())

    logger2.error(666)

    明明只想打印一次666，结果却答应2次了。因为a.b的父命名空间的日志也加了streamhandler。

    :param self:
    :param record:
    :return:
    """

    """
    Pass a record to all relevant handlers.

    Loop through all handlers for this logger and its parents in the
    logger hierarchy. If no handler was found, output a one-off error
    message to sys.stderr. Stop searching up the hierarchy whenever a
    logger with the "propagate" attribute set to zero is found - that
    will be the last logger whose handlers are called.
    """
    c = self
    found = 0
    hdlr_type_set = set()

    while c:
        for hdlr in c.handlers:
            hdlr_type = type(hdlr)
            if hdlr_type == logging.StreamHandler:  # REMIND 因为很多handler都是继承自StreamHandler，包括filehandler，直接判断会逻辑出错。
                hdlr_type = ColorHandler
            found = found + 1
            if record.levelno >= hdlr.level:
                if hdlr_type not in hdlr_type_set:
                    hdlr.handle(record)
                hdlr_type_set.add(hdlr_type)
        if not c.propagate:
            c = None  # break out
        else:
            c = c.parent
    # noinspection PyRedundantParentheses
    if (found == 0):
        if logging.lastResort:
            if record.levelno >= logging.lastResort.level:
                logging.lastResort.handle(record)
        elif logging.raiseExceptions and not self.manager.emittedNoHandlerWarning:
            sys.stderr.write("No handlers could be found for logger"
                             " \"%s\"\n" % self.name)
            sys.stderr.flush()
            self.manager.emittedNoHandlerWarning = True


# noinspection PyProtectedMember
def revision_add_handler(self, hdlr):  # 从添加源头阻止同一个logger添加同类型的handler。
    """
    Add the specified handler to this logger.
    """
    logging._acquireLock()  # noqa

    try:
        """ 官方的
        if not (hdlr in self.handlers):
            self.handlers.append(hdlr)
        """
        hdlrx_type_set = set()
        for hdlrx in self.handlers:
            hdlrx_type = type(hdlrx)
            if hdlrx_type == logging.StreamHandler:  # REMIND 因为很多handler都是继承自StreamHandler，包括filehandler，直接判断会逻辑出错。
                hdlrx_type = ColorHandler
            hdlrx_type_set.add(hdlrx_type)

        hdlr_type = type(hdlr)
        if hdlr_type == logging.StreamHandler:
            hdlr_type = ColorHandler
        if hdlr_type not in hdlrx_type_set:
            self.handlers.append(hdlr)
    finally:
        logging._releaseLock()  # noqa


logging.Logger.callHandlers = revision_call_handlers  # 打猴子补丁。
logging.Logger.addHandler = revision_add_handler      # 打猴子补丁。