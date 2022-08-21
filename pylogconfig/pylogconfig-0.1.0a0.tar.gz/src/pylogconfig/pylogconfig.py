import logging.config


def config_logger(cfg):
    if isinstance(cfg, dict):
        _config_logger_from_dict(cfg)
    else:
        raise TypeError


def _config_logger_from_dict(config_dict):
    logging.config.dictConfig(config_dict)


def _config_logger_from_toml(config_toml_path):
    # https://pypi.org/project/toml/
    raise NotImplementedError


def _config_logger_from_yaml(config_yaml_path):
    # https://omegaconf.readthedocs.io/en/2.2_branch/
    raise NotImplementedError


def _config_logger_from_conf(config_conf_path):
    # https://docs.python.org/3/library/logging.config.html#logging.config.fileConfig
    # https://docs.python.org/3/library/configparser.html#module-configparser
    raise NotImplementedError


def _config_logger_from_ini(config_yaml_path):
    # same as from conf
    raise NotImplementedError
