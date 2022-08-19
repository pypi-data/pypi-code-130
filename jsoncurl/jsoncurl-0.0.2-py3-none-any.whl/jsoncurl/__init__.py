#!/usr/bin/env python
import ast
import sys
from typing import Callable, Dict, List, Optional, Set, Tuple, Union

import requests
from rich import print


def extract_url(args: List[str]) -> str:
    return next(filter(lambda x: x.startswith('http'), args), None)


def extract_json_input(args: List[str]) -> Dict:
    res = {}
    for arg in args:
        if '=' not in arg:
            try:
                js = ast.literal_eval(arg)
                return js
            except Exception as e:
                continue
        else:
            key, value = arg.split('=')
            res[key] = value
    return res


def jsoncurl():
    args = sys.argv[1:]
    url = extract_url(args)
    if url is None:
        print('url not found, url must start with http(s)')
        return
    json_input = extract_json_input(args)
    if not json_input:
        print('json input not found')
        return

    msg = {'url': url, 'json_input': json_input}
    print(msg)
    resp = requests.post(url, json=json_input)

    try:
        print(resp.json())
    except Exception as e:
        print(e)
        print(resp.text)
