import logging
import re as regex_extractor
import traceback

from newtools.optional_imports import json_log_formatter

"""
Constant keys for the persistent fields to be logged by every application.
"""
APPLICATION_DOMAIN_KEY = 'application_domain'
APPLICATION_NAME_KEY = 'application_name'
APPLICATION_REQUEST_ID_KEY = 'application_request_id'
TOTAL_EXEC_TIME_IN_SECS_KEY = 'total_execution_time_in_secs'
START_TIME_KEY = 'start_time'
END_TIME_KEY = 'end_time'

"""
Constants used by the logger library to extract and save the error details to the error log message.
"""
CLASS_NAME = 'ClassName'
ERROR_MESSAGE = 'ErrorMessage'
ERROR_STACK_TRACE = 'ErrorStackTrace'
DEFAULT_CLASS_NAME = 'None'

CLASS_NAME_SEARCH_PATTERN = "<class '([^\'>]+)"


def _extract_exception(exception_details_dict, exception_object):
    """
    This function adds the exception extracted details to the log message. This function
    overrides the current exception stack details persisted with the new exception stack details if
    provided any.

    :param exception_object: exception object to retrieve exception details and stack trace.
    """
    class_name_search = regex_extractor.search(CLASS_NAME_SEARCH_PATTERN, str(type(exception_object)))

    exception_details_dict[CLASS_NAME] = class_name_search.group(1) if class_name_search else DEFAULT_CLASS_NAME
    exception_details_dict[ERROR_MESSAGE] = str(exception_object)
    exception_details_dict[ERROR_STACK_TRACE] = str(traceback.format_exc())


class JSONLogger:
    """
    This is a wrapper of logging library where the logs are displayed in the json format.

    This wrapper has the feature of Persistent logging and can be used optionally as well.
    """

    def __init__(self, logger_name, logging_level=logging.INFO, log_file_path=None):
        """
        This class creates a logging instance with json formatted messages and adds an optional feature
        for persisting any fields onto the log messages as and when required.

        :param logger_name: Any string with valid understandable name.
        :param logging_level: Any kind of logging level from where the lowest prioritized log level is required
            if used logging.DEBUG - All levels Debug, Info, Warning and Error logs are logged.
            if used logging.INFO - levels Info, Warning and Error logs are logged.
            if used logging.WARNING - levels Warning and Error logs are logged.
            if used logging.ERROR - Only Error logs are logged.
        :param log_file_path: In case to save the logs onto a json file.
        """
        self.persistent_fields = dict()

        logger_instance = logging.getLogger(logger_name)
        logger_instance.handlers.clear()
        logger_instance.setLevel(logging_level)

        self.json_formatter = json_log_formatter.JSONFormatter()

        if log_file_path is None:
            generic_handler = logging.StreamHandler()
        else:
            generic_handler = logging.FileHandler(log_file_path)
        generic_handler.setFormatter(self.json_formatter)

        logger_instance.addHandler(generic_handler)
        self.log_instance = logger_instance

    def remove_persistent_field(self, field_name):
        """
        This function helps in removing a key value pair to the persistent field dictionary.

        :param field_name: key to be removed from the persistent field dictionary.

        :return: None
        """
        self.persistent_fields.pop(field_name, None)

    def remove_all_persistent_fields(self):
        """
        This function helps in removing all key value pairs in the persistent field dictionary.

        :return: None
        """
        self.persistent_fields = dict()

    def add_persistent_field(self, field_name, field_value):
        """
        This function helps in adding a key value pair to the persistent field dictionary.

        :param field_name: key to be saved in the persistent field dictionary.
        :param field_value: value to be saved for the given key

        :return: None
        """
        self.persistent_fields[field_name] = field_value

    def add_persistent_fields(self, **fields):
        """
        This function helps in adding a set of key value pairs to the persistent field dictionary.

        :param fields: A set of keyword arguments to be saved to the persistent field dictionary.

        :return: None
        """
        self.persistent_fields = {**self.persistent_fields, **fields}

    def _handle_log_parameters(self, excess_persistent_dict, kwargs):
        """
        This function adds excess persistent fields provided to the debug, info, error, warning. Apart from that
        any excess non-persistent fields passed to the below methods will be logged but not persisted.

        :param excess_persistent_dict: excess persistent dict to be added to instance persistence dictionary.
        :param kwargs: Excess non-persistent dict to be logged with the log message called for with below methods.

        :return: All persistent and non-persistent key value pairs which are to be logged.
        """
        if excess_persistent_dict is not None:
            self.add_persistent_fields(**excess_persistent_dict)
        logging_params = {**self.persistent_fields, **kwargs}
        return logging_params

    def debug(self, message, excess_persistent_dict=None, **kwargs):
        logging_params = self._handle_log_parameters(excess_persistent_dict, kwargs)
        self.log_instance.debug(message, extra=logging_params)

    def info(self, message, excess_persistent_dict=None, **kwargs):
        logging_params = self._handle_log_parameters(excess_persistent_dict, kwargs)
        self.log_instance.info(message, extra=logging_params)

    def warning(self, message, excess_persistent_dict=None, **kwargs):
        logging_params = self._handle_log_parameters(excess_persistent_dict, kwargs)
        self.log_instance.warning(message, extra=logging_params)

    def error(self, message, excess_persistent_dict=None, exception_object=None, **kwargs):
        exception_details_dict = dict()
        if exception_object is not None:
            _extract_exception(exception_details_dict, exception_object)

        logging_params = self._handle_log_parameters(excess_persistent_dict, {**kwargs, **exception_details_dict})
        self.log_instance.error(message, extra=logging_params)
