# Copyright 2022 The PrimeQA Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools
import logging
import multiprocessing
import os
import traceback
from argparse import ArgumentTypeError
from configparser import ConfigParser
from distutils.util import strtobool
from importlib import import_module
from os import environ
from typing import Union, Callable, Type, Optional, Any, get_type_hints

from pkg_resources import resource_filename

_ENVIRONMENT_VARIABLE = 'config_override_section'
_CONFIG_FILE = resource_filename("config", "config.ini")

def positive_integer_type(value):
    try:
        ivalue = int(value)
    except ValueError as ex:
        raise ArgumentTypeError(
            '%s is an invalid positive int value: %s' % (value, ex)) from ex

    if ivalue < 1:
        raise ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue



class ConfigurationError(Exception):
    def __init__(self, message):
        help_message = "You can override config parameters in the config file '{}', setting the " \
                       "'{}' environment variable to a config file target, or by setting the " \
                       "environment variable with the same name (environment variables override config).".format(
            _CONFIG_FILE, _ENVIRONMENT_VARIABLE
        )
        super().__init__("{} -- {}".format(message, help_message))


class ConfigurationTypeError(ConfigurationError, TypeError):
    pass


class ConfigurationLookupError(ConfigurationError, LookupError):
    pass


def config_value(property_type: Union[Callable, Type] = str, default: Optional[Any] = None,
                 is_secret: bool = False) -> Callable:
    """
    Decorator factory for Settings config values.

    Example of an int parameter which will default to 42:

    ```python
    @config_value(property_type: int, default: 42)
    def foo(self): pass
    ```

    Note that if calling with default arguments it must be called as @config_value().

    :param Union[Callable, Type] property_type: called with the property string value to create final property value
    :param Optional[Any] default: default value of the parameter if no value in config, if None the value is required
    :param bool is_secret: omits sensitive (True) values from dictionary view
    :return: decorator for a config value
    :rtype: Callable
    """
    def outer_wrapper(f: Callable) -> property:
        property_type_hints = get_type_hints(property_type)
        if isinstance(property_type, type):
            return_type = property_type
        elif "return" in property_type_hints:
            return_type = property_type_hints["return"]
        else:
            return_type = Any

        @property
        @functools.wraps(f)
        def inner_wrapper(self: "Settings", *args, **kwargs) -> return_type:
            property_name = f.__name__
            return self._get_or_process_config_value(property_name, property_type, default, is_secret)
        return inner_wrapper
    return outer_wrapper


def class_reference(class_reference_as_str: str) -> Type:
    """
    Given a fully qualified path to a class reference, return a pointer to the class reference
    :param str class_reference_as_str: the fully qualified path (expects the fully qualified
        path in dot notation, e.g. <<gaama.business.featurizers.nq_featurizer.NQFeaturizer>>)
    :return: class
    :rtype: Type
    """
    try:
        module_name, class_name = _split_into_class_and_module_name(class_reference_as_str)
        module_reference = import_module(module_name)
        if class_name is None:
            return module_reference
        else:
            return getattr(module_reference, class_name)
    except Exception as ex:
        traceback.print_exc()  # Shows additional traceback for why imports fail
        raise ConfigurationError('Unable to resolve the string <<%s>> to a fully qualified class path (expects '
                                 'the fully qualified path in dot notation, e.g.'
                                 ' <<gaama.business.featurizers.nq_featurizer.NQFeaturizer>>): %s' %
                                 (class_reference_as_str, repr(ex))) from ex


def _split_into_class_and_module_name(class_path):
    modules = class_path.split('.')
    if len(modules) > 1:
        return ".".join(modules[:-1]), modules[-1]
    else:
        return class_path, None


def probability_float(value) -> float:
    value = float(value)
    if not (0. <= value <= 1.):
        raise ValueError("Expected 0 <= value <= 1 but was {}".format(value))
    return value


def str_or_file(value: str) -> str:
    if os.path.isfile(value):
        with open(value, 'r') as f:
            return f.read().strip()
    else:
        return value


class Settings(object):
    """
    Helper class wraps config/config.ini and returns the parameter
        settings for the section referenced in the environment variable
        for `environment`. If no such environment variable is set,
        then uses the default section of the config.

    Also checks environment variables to see if there are any overrides,
    if so, will use those instead of the values from the config file.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        if logger is None:
            self._logger = logging.getLogger(self.__class__.__name__)
        else:
            self._logger = logger

        self._config_value_cache = {}
        self._raw_config_values = self._load_settings_from_config_and_env_vars()
        self._is_config_value_secret = {}
        self._logger.info("Settings loaded with value: {}".format(self))

    @config_value(property_type=positive_integer_type)
    def max_answer_length(self): pass

    @config_value(property_type=positive_integer_type)
    def predict_batch_size(self): pass

    @config_value(property_type=positive_integer_type)
    def port(self): pass

    @config_value(property_type=positive_integer_type)
    def num_server_threads(self): pass

    @config_value(property_type=positive_integer_type, default=multiprocessing.cpu_count())
    def num_worker_processes(self): pass

    @config_value(property_type=bool)
    def no_cuda(self): pass

    @config_value(property_type=positive_integer_type)
    def max_seq_length(self): pass

    @config_value(property_type=positive_integer_type)
    def max_query_length(self): pass

    @config_value(property_type=positive_integer_type)
    def doc_stride(self): pass

    @config_value(property_type=bool)
    def deterministic(self): pass

    @config_value(property_type=positive_integer_type, default=multiprocessing.cpu_count())
    def num_pytorch_threads(self): pass

    @config_value(property_type=int)
    def seed(self): pass

    @config_value(property_type=bool)
    def fp16(self): pass

    @config_value()
    def span_tracker_type(self): pass

    @config_value()
    def final_short_answer_scorer(self): pass

    @config_value(property_type=positive_integer_type)
    def n_best_size(self): pass

    @config_value(property_type=probability_float)
    def target_type_weight(self): pass

    @config_value()
    def model_name_or_path(self): pass

    @config_value(property_type=class_reference)
    def model_class(self): pass

    @config_value(property_type=class_reference)
    def model_provider_class(self): pass

    @config_value(property_type=str_or_file)
    def modeling_notes(self): pass

    @config_value()
    def tokenizer_name_or_path(self): pass

    @config_value(property_type=class_reference)
    def tokenizer_class(self): pass

    @config_value(property_type=class_reference)
    def featurizer_class(self): pass

    @config_value(property_type=class_reference)
    def predictor_class(self): pass

    @config_value(property_type=class_reference)
    def predictor_span_tracker(self): pass

    @config_value(property_type=bool)
    def disable_space_prefix_in_gpt2_tokenizer(self): pass

    @config_value()
    def cos_endpoint(self): pass

    @config_value(is_secret=True)
    def cos_access_key(self): pass

    @config_value(is_secret=True)
    def cos_secret_key(self): pass

    @config_value()
    def cos_model_filename(self): pass

    @config_value()
    def cos_tokenizer_filename(self): pass

    @config_value()
    def cos_bucket(self): pass

    @config_value()
    def cos_local_cache(self): pass

    @config_value(property_type=bool)
    def use_research_ssl_cert(self): pass

    @config_value(default=resource_filename("scripts", "health-check.sh"))
    def health_check_script(self): pass

    @config_value(property_type=float)
    def normalization_beta0(self): pass

    @config_value(property_type=float)
    def normalization_beta1(self): pass

    @config_value(property_type=bool)
    def use_score_normalization(self): pass

    @config_value()
    def statsd_host(self): pass

    @config_value(property_type=int)
    def statsd_port(self): pass

    @config_value(property_type=str)
    def statsd_prefix(self): pass

    @config_value(property_type=bool)
    def submit_metrics(self): pass

    @config_value(property_type=int)
    def grpc_max_connection_age_secs(self): pass

    @config_value(property_type=int)
    def grpc_max_connection_age_grace_secs(self): pass

    # Begin TechQA Params
    @config_value(property_type=bool)
    def add_doc_title_to_passage(self): pass

    @config_value(property_type=bool)
    def use_query_title_only(self): pass

    @config_value(property_type=bool)
    def use_query_body_only(self): pass

    @config_value(property_type=bool)
    def drop_stop_words_from_query(self): pass

    @config_value(property_type=str)
    def passage_delimiter(self): pass

    @config_value(property_type=set)
    def exclude_metrics_for_txn_ids(self): pass

    # End TechQA Params

    def _get_config_dict(self):
        config_dict = {}
        for property_name in dir(self):
            if property_name.startswith('_'):
                continue

            try:
                property_value = getattr(self, property_name)
                if self._is_config_value_secret[property_name]:
                    property_value = "*********"
            except ConfigurationLookupError:
                property_value = None

            config_dict[property_name] = property_value
        return config_dict

    def __repr__(self):
        config_dict = self._get_config_dict()
        return "{}({!r})".format(self.__class__, config_dict)

    def __str__(self):
        config_dict = self._get_config_dict()
        return "{}({})".format(self.__class__.__name__, config_dict)

    def _load_settings_from_config_and_env_vars(self):
        settings_from_config_file = ConfigParser(allow_no_value=True, interpolation=None)
        self._logger.debug('Reading default settings from <%s>' % _CONFIG_FILE)
        settings_from_config_file.read(_CONFIG_FILE)

        if _ENVIRONMENT_VARIABLE in environ:
            environment = environ[_ENVIRONMENT_VARIABLE]
            if environment not in settings_from_config_file:
                environment = settings_from_config_file.default_section
        else:
            environment = settings_from_config_file.default_section

        self._logger.info('Initializing settings with values for <%s>' % environment)
        settings = settings_from_config_file[environment]

        return self._update_with_environment_variable_overrides(settings)

    def _update_with_environment_variable_overrides(self, config):
        for key, value in config.items():
            if key in environ:
                self._logger.debug('Updating the default value of %s with env var override: %s' %
                                   (key, environ[key]))
                config[key] = environ[key]
        return config

    def _get_or_process_config_value(self, property_name: str, property_type: Union[Callable, Type],
                                     default: Optional[Any], is_secret: bool) -> Any:
        # see @config_value decorator factory docstring for details
        if property_name not in self._config_value_cache:
            self._is_config_value_secret[property_name] = is_secret

            if self._raw_config_values[property_name] is None and default is None:
                raise ConfigurationLookupError("Missing property {}".format(property_name))

            property_value = self._raw_config_values.get(property_name, None)
            if property_value is not None:
                try:
                    logging.debug("Attempting to construct value for {}".format(property_name))
                    if property_type == bool:
                        property_value = bool(strtobool(property_value))  # bool('False') == True
                    elif property_type == set:
                        property_value = set(map(str.strip, property_value.split(",")))
                    else:
                        property_value = property_type(property_value)
                except Exception as ex:
                    raise ConfigurationTypeError(
                        "Unable to convert property {} with value {} to type {}".format(property_name,
                                                                                        property_value,
                                                                                        property_type)) from ex
            else:
                logging.debug("Using default value for {}".format(property_name))
                property_value = default
            self._config_value_cache[property_name] = property_value
        return self._config_value_cache[property_name]
