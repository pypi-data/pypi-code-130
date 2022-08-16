import logging
import os
import datetime


def check_and_create_folder(logFolder):
    """
     Check for log folder existance. If not creates it
    :param logFolder: path for logfolder
    :return: foldername(str)
    """
    today = datetime.datetime.now().strftime('%b-%d-%G')
    isExist = os.path.exists(logFolder)
    if not isExist:
        os.makedirs(logFolder)
    foldername = os.path.join(logFolder, str(today))
    if not os.path.exists(foldername):
        os.mkdir(foldername)
    return foldername


class LoggerFactory(object):
    _LOG = None

    @staticmethod
    def __create_logger(log_file, log_level):
        """
        A private method that interacts with the python
        logging module

        :param log_file: log file path
        :param log_level: logging level
        :return: logger._Log (logger object)
        """

        filepath = "logs"
        folderName = check_and_create_folder(filepath)

        # set the logging format
        log_format = "'%(asctime)s | %(name)s  | %(levelname)s  | %(message)s'"

        # Initialize the class variable with logger object
        LoggerFactory._LOG = logging.getLogger(log_file)
        logging.basicConfig(filename=os.path.join(folderName, "logs.log"),
                            filemode='a', level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")

        # set the logging level based on the user selection
        if log_level == "INFO":
            LoggerFactory._LOG.setLevel(logging.INFO)
        elif log_level == "ERROR":
            LoggerFactory._LOG.setLevel(logging.ERROR)
        elif log_level == "DEBUG":
            LoggerFactory._LOG.setLevel(logging.DEBUG)
        return LoggerFactory._LOG

    @staticmethod
    def get_logger(log_file, log_level):
        """
        A static method called by other modules to initialize logger in
        their own module
        :param log_file: log file path
        :param log_level: logging level
        :return: logger (logger object)
        """
        logger = LoggerFactory.__create_logger(log_file, log_level)

        # return the logger object
        return logger