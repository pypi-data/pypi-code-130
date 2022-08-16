# coding: utf-8
from typing import Sequence
import json
import urllib
import os
from jsonpath import jsonpath
from tqdm import tqdm
import logging
logging.root.setLevel("INFO")
logging.debug("Запись.")

def chunks(l: Sequence, win_len: int, stride_len: int, bak_id: int):
    s_id = 0
    if bak_id != 0:
        s_id = bak_id + 1
    e_id = min(len(l), win_len)

    while True:
        if s_id != e_id:
            yield l[s_id:e_id]
            s_id = s_id + stride_len

        if e_id == len(l):
            break

        e_id = min(s_id + win_len, len(l))

def load_json(file):
    with open(file, "r", encoding='utf-8') as f:
        data = json.load(f)
    return data

def save_json(jsondata, file):
    if not os.path.exists(file):
        os.makedirs(file.rsplit('/', 1)[0], exist_ok=True)
    with open(file, "w", encoding='utf-8') as f:
        json.dump(jsondata, f, ensure_ascii=False, indent=2)

def download_img(img):
    try:
        request = urllib.request.Request(img)
        response = urllib.request.urlopen(request)
        get_img = response.read()
        save_dir = "download_images/"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        with open('download_images/{}'.format(img.split('/')[-1]), 'wb') as f:
            f.write(get_img)
    except Exception:
        logging.info('{} 路径无效, 这个图片路径不存在！'.format(img))

def get_pic_urls(data_path):
    data = load_json(data_path)
    urls = jsonpath(data, "$..url")
    for id, url in enumerate(tqdm(urls)):
        data[id]['id'] = id

    return urls, data