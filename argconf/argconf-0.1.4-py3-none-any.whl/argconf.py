import argparse
from collections import OrderedDict
from pyhocon import ConfigFactory
from box import Box
import importlib

def instantiate_from_config(config):
    if not "target" in config:
        raise KeyError("Expected key `target` to instantiate.")
    return get_obj_from_str(config["target"])(**config.get("params", dict()))


def get_obj_from_str(string, reload=False):
    module, cls = string.rsplit(".", 1)
    if reload:
        module_imp = importlib.import_module(module)
        importlib.reload(module_imp)
    return getattr(importlib.import_module(module, package=None), cls)


def _convert_str(s):
    try:
        return int(s)
    except:
        pass
    try:
        return float(s)
    except:
        pass
    return s


def _resolve_fields(sub_conf, prefix=None):
    complete_fields = dict()
    for k in sub_conf:
        if prefix is None:
            new_prefix = k
        else:
            new_prefix = f"{prefix}.{k}"
        if isinstance(sub_conf[k], OrderedDict):
            complete_fields.update(_resolve_fields(sub_conf[k], new_prefix))
        else:
            complete_fields[new_prefix] = type(sub_conf[k])
    return complete_fields


def _convert_arg(val, conversion):
    if conversion == "str2list":
        val_list = val.strip().replace("]", "").replace("[", "").replace(")", "").replace("(", "").split(",")
        val_list = [_convert_str(s) for s in val_list]
        return val_list
    else:
        return val


def _update_subdict(subdict, key, val):
    if "." in key:
        subkeys = key.split(".")
        _update_subdict(subdict[subkeys[0]], ".".join(subkeys[1:]), val)
    else:
        subdict[key] = val


def _convert_none(conf):
    for k,v in conf.items():
        if type(v)==Box:
            conf[k] = _convert_none(v)
        else:
            if v == "None":
                conf[k] = None
    return conf

def argconf_parse(conf_fn=None):

    if conf_fn is None:
        # load config name
        # support [--conf and first argument]
        conf_parser = argparse.ArgumentParser()
        conf_parser.add_argument("conf", type=str)
        conf_args = conf_parser.parse_known_args()[0]
        CONF_OPTIONAL = "--conf" in conf_parser.parse_known_args()[1]
        conf = ConfigFactory.parse_file(conf_args.conf)
    else:
        # load specific configuration
        conf = ConfigFactory.parse_file(conf_fn)
        CONF_OPTIONAL = True

    # load config
    parser = argparse.ArgumentParser()
    # parser.add_argument("--conf", type=str)
    if CONF_OPTIONAL:
        parser.add_argument("--conf", type=str)
    else:
        parser.add_argument("conf", type=str)
    # parser.add_argument("--conf", type=str)

    complete_fields = _resolve_fields(conf)  # nested . notation

    # create short names for reference
    shorted_fields = dict()
    suffix_list = [complete_name.split(".")[-1] for complete_name in complete_fields]
    short2complete = dict()

    for complete_name, field_type in complete_fields.items():
        suffix = complete_name.split(".")[-1]
        if suffix_list.count(suffix) == 1:
            shorted_fields[suffix] = field_type
            short2complete[suffix] = complete_name
        else:
            shorted_fields[complete_name] = field_type
            short2complete[complete_name] = complete_name

    convert_dict = dict()
    # create arguments for argparse with short/complete names
    for short_name, field_type in shorted_fields.items():
        complete_name = short2complete[short_name]
        if field_type in [str, int, float]:
            parser.add_argument(f"-{short_name}", f"-{complete_name}", type=field_type)
        if field_type == type(None):
            parser.add_argument(f"-{short_name}", f"-{complete_name}", type=str)

        if field_type == bool:
            parser.add_argument(f"-{short_name}", f"-{complete_name}", action="store_true")
        if field_type in [list, tuple]:
            parser.add_argument(f"-{short_name}", f"-{complete_name}", type=str)
            convert_dict[short_name] = "str2list"

    args = parser.parse_args()
    # load argparse arguments and convert fields
    for arg_name, arg_val in args._get_kwargs():
        if arg_name == "conf":
            conf["conf"] = arg_val
        elif arg_val is not None and (shorted_fields[arg_name] is not bool or arg_val):
            if arg_name in convert_dict:
                arg_val = _convert_arg(arg_val, convert_dict[arg_name])
            _update_subdict(conf, short2complete[arg_name], arg_val)

    # return box object with nested . access
    conf = Box(conf, box_dots=True)
    # convert "None" to None ()
    conf = _convert_none(conf)
    return conf

