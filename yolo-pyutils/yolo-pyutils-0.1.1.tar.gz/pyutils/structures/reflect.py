import importlib

CONF_KEY_CLASS = "class"
CONF_KEY_INIT_ARGS = "args"
reflect_cache = {}


def generate_instance(clazz_dict, init_args_origin_dict):
    clazz = clazz_dict.get(CONF_KEY_CLASS)
    if clazz is None:
        raise RuntimeError("'{}' field is required".format(CONF_KEY_CLASS))
    init_args_dict = init_args_origin_dict
    init_args = clazz_dict.get(CONF_KEY_INIT_ARGS)
    if init_args is not None:
        init_args_dict.update(init_args)
    constructor_fn = reflect_fn(clazz)
    return constructor_fn(**init_args_dict)


def reflect_fn(fn_path):
    global reflect_cache
    fn = reflect_cache.get(fn_path)
    if fn is None:
        tmp_arrays = fn_path.rsplit('.', 1)
        # directly return eval function if no module defined
        if len(tmp_arrays) == 1:
            return eval(fn_path)
        mod = importlib.import_module(tmp_arrays[0])
        fn = getattr(mod, tmp_arrays[1])
        reflect_cache[fn_path] = fn
    return fn
