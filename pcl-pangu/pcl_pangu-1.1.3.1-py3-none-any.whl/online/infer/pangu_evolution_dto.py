#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Date: 2022/8/17
# @Author: pcl

class PanguEvolutionDTO(object):

    DEFAULT_MAX_TOKEN = 50
    TOP_P = 0.0
    TOP_K = 1

    def __init__(self):
        pass

    @classmethod
    def build_request(cls, prompt_input, max_token, top_p, top_k):
        max_token = cls.DEFAULT_MAX_TOKEN if max_token is None else max_token
        top_p = cls.TOP_P if top_p is None else top_p
        top_k = cls.TOP_K if top_k is None else top_k

        request = {"u": prompt_input,
                   "result_len": max_token,
                   "top_p": top_p,
                   "top_k": top_k,
                   "task_name": ""
                   }
        return request

    @classmethod
    def build_default_response(cls, api_key, model, prompt_input):
        default_response = {
            "id": api_key,
            "model": model,
            "object": "generate",
            "results": {
                "prompt_input": prompt_input,
                "generate_text": None,
                "logprobs": None,
            },
            "status": False
        }
        return default_response