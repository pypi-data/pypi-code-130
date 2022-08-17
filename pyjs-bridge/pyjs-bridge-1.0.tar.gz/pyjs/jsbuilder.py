from jsmin import jsmin
import os
import json
from .registry import get_all_exposed_interfaces
from .pillar import get_js_prototype


# def build_body(body_params):
#     if len(body_params) == 1:
#         return body_params[0]
#     out = "{"
#     for p in body_params:
#         out = out + "\"" + p + "\":" + p + ","
#     out = out + "}"
#     out = out.replace(",}", "}")
#     return out


def convert_to_js_structure(proxy):
    function_list = ""
    for name, item in proxy.items():
        if isinstance(item, str):
            function_list = function_list + "\"" + name + "\":" + item + ","
        else:
            function_list = function_list + "\"" + name + "\": {" + convert_to_js_structure(item) + "},"
    return function_list


def build_javascript():
    server_proxy = {}
    for name, signature, doc in get_all_exposed_interfaces():
        pd = None
        for optional_index, (p, t, d) in enumerate(signature):
            if pd is None and d is not None:
                break
            pd = d

        args_string = [(p + ("" if d is None and i < optional_index else "=" + json.dumps(d))) for i, (p, t, d) in enumerate(signature)]
        args_obj = [("\"" + p + "\":" + p) for p, t, d in signature]
        args_obj = "{" + ",".join(args_obj) + "}"

        function_str = "function(" + ",".join(args_string) + ") {" + "return send(\"" + name + "\"," + args_obj + ")}"

        ptr = server_proxy
        parts = name.split(".")
        for i in range(len(parts) - 1):
            if parts[i] not in server_proxy:
                server_proxy[parts[i]] = {}
            ptr = server_proxy[parts[i]]
        ptr[parts[len(parts) - 1]] = function_str

    function_list = convert_to_js_structure(server_proxy)
    function_list = function_list + "\"version\": \"0.0.1\""
    content = get_js_prototype()
    content = content.replace("//<%functions>", function_list)
    minified = jsmin(content)
    return minified
