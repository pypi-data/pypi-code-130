from configparser import ConfigParser


def to_boolean(value):
    return str(value).lower() == "true"


_defaultValues = {
    "enable_sql_trace": True,
}

_valueFunc = {
    "enable_sql_trace": to_boolean,
}


class AppConfig(object):
    def __init__(self, config_path):
        self.path = None
        self.config = None
        self.load_config(config_path)

    def __getattr__(self, item):
        if self.config is None:
            return None

        try:
            value_func = _valueFunc[item]
            default_value = _defaultValues[item]

            if default_value is None:
                return None

            current_value = self.config['JENNIFER'].get(item, default_value)

            if value_func is None:
                return current_value

            return value_func(current_value)
        except:
            return None

    def reload(self):
        self.load_config(self.path)

    def load_config(self, config_path):
        if config_path is None:
            return

        try:
            self.path = config_path

            self.config = ConfigParser()
            self.config.read(config_path)
        except:
            pass

