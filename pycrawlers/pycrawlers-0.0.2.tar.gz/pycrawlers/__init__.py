# -*- coding: UTF-8 -*-
# @Time : 2022/8/17 16:01 
# @Author : 刘洪波

from pycrawlers.Hugging_Face.download import HuggingFace


def huggingface(base_url: str = None):
    return HuggingFace(base_url)
