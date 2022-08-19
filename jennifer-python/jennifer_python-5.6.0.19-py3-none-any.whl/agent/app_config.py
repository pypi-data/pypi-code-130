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

    def __getattr__(self, attr_name):
        if self.config is None:
            return None

        try:
            value_func = _valueFunc[attr_name]
            default_value = _defaultValues[attr_name]

            if default_value is None:
                return None

            if not self.config.has_option('JENNIFER', attr_name):
                attr_value = self.config['SERVER'].get(attr_name, default_value)
            else:
                attr_value = self.config['JENNIFER'].get(attr_name, default_value)

            if value_func is None:
                return attr_value

            return value_func(attr_value)
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

