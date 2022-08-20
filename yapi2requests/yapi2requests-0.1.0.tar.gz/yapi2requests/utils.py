import json
import re


def build_test_name_from_path(path):
    re_expr = "[a-zA-Z0-9]+"
    find_paths = re.findall(re_expr, path)
    test_class_name = "".join([v.capitalize() for v in find_paths])
    test_func_name = "_".join(find_paths)
    return test_class_name, test_func_name


def replace_json_data_to_python_obj(requests_des):
    for key in requests_des.keys():
        if requests_des.get(key) and key in ["headers", "params", "json", "data"]:
            requests_des[key] = json.dumps(requests_des[key], ensure_ascii=False, indent=16) \
                .replace('null', 'None') \
                .replace('true', 'True') \
                .replace('false', 'False')

