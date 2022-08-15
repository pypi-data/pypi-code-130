global_variables = {}


def set_var(name: str, value):
    global_variables[name] = value


def get_var(name: str):
    return global_variables[name]
