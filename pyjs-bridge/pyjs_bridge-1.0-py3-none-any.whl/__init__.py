from .decorator import *
import sys
import warnings
import os
import json
from .registry import mock_incoming, get_active_client_info, get_all_exposed_interfaces
from .pillar import initialize, start_listener, stop_listener
from .jsbuilder import build_javascript


def find_optional_index(args):
    pd = None
    for optional_index, (p, t, d) in enumerate(args):
        if pd is None and d is not None:
            break
        pd = d
    return optional_index


def arg_pretty_print(arg, t, d, optional=False):
    return "**" + arg + "** : " + (t.__name__ if t is not None else "any") + ("" if not optional else " = " + ("undefined" if d is None else json.dumps(d)))


def generate_md_api_doc():

    md_text = ""
    md_text += "## Server functions<br>  \n"
    md_text += "  \n"
    for n, args, doc in get_all_exposed_interfaces():
        md_text += "- **" + n + "**("
        optional_index = find_optional_index(args)
        md_text += ", ".join([arg_pretty_print(arg, t, d, optional_index <= i) for i, (arg, t, d) in enumerate(args)])
        md_text += ")  \n"
        md_text += "\t" + doc + "  \n"
        md_text += "  \n"

    md_text += "  \n"
    md_text += "## Client callbacks  \n"
    md_text += "  \n"
    for n, args, doc in get_active_client_info():
        md_text += "- **" + n + "**("
        optional_index = find_optional_index(args)
        md_text += ", ".join([arg_pretty_print(arg, t, d, optional_index <= i) for i, (arg, t, d) in enumerate(args)])
        md_text += ")  \n"
        md_text += "\t" + doc + "  \n"
        md_text += "  \n"

    return md_text
