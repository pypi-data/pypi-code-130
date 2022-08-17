# -*- coding: UTF-8 -*-
# @Time : 2022/8/17 15:40 
# @Author : 刘洪波
import requests
from tqdm import tqdm
from lxml import etree
import os


# 爬取网页
def crawl_html(url: str, headers: dict):
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        res_html = etree.HTML(response.content)
        return res_html
    else:
        raise Exception(f'the status_code of response is {str(response.status_code)}, '
                        f'failed to get data, your url is {url}')


# 下载数据
def download(url: str, fname: str, headers: dict):
    resp = requests.get(url, headers=headers, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
        desc=fname,
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


def juedge_path(file_path: str):
    """判断路径是否存在，不存在就创建"""
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    if file_path[-1] != '/':
        file_path += '/'
    return file_path


def juedge_url(url: str):
    """url检查"""
    if 'http://' not in url and 'https://' not in url:
        raise ValueError(f'URL error, the url is missing http or https, your url is {url}')
