#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Date: 2022/8/17
# @Author: pcl
import requests
import time

default_response = {
    "id": None,
    "model": None,
    "object": "generate",
    "results": {
        "prompt_input": None,
        "generate_text": None,
        "logprobs": None,
    },
    "status": True
}

def reset_default_response():
    global default_response
    default_response = {
        "id": None,
        "model": None,
        "object": "generate",
        "results": {
            "prompt_input": None,
            "generate_text": None,
            "logprobs": None,
        },
        "status": True
    }

def send_requests_pangu_alpha(payload):
    global default_response
    response = requests.get('https://pangu-alpha.openi.org.cn/query?', params=payload)
    if response.status_code == 200:
        result = response.json()['rsvp']
        if result is None:
            payload['isWaiting'] = 'true'
            time.sleep(10)
            send_requests_pangu_alpha(payload)
        else:
            default_response['results']['prompt_input'] = payload['u']
            default_response['results']['generate_text'] = result[-1]
    else:
        default_response['status'] = False
        print("Error response! checkout your [url] is 'https://pangu-alpha.openi.org.cn/query?'\n")

def get_response():
    return default_response