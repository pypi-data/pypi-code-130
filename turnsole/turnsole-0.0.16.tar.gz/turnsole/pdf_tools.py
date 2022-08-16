# -*- coding: utf-8 -*-
# @Author        : Lyu Kui
# @Email         : 9428.al@gmail.com
# @Create Date   : 2021-12-22 11:00:28
# @Last Modified : 2021-12-22 11:48:39
# @Description   : 

import cv2
import fitz
import json
import base64
import requests
import numpy as np
from PIL import Image

import tensorflow as tf

import matplotlib.pyplot as plt

def image_in_page(page):
    # 判断 PDF 某一页是否是插图形式，默认不是
    # 判断依据较为复杂，只有所有苛刻的条件满足时才判定为插图形式，否则下一步将执行整页 PDF 转 Image
    # 首先要求页面中一个字都没有
    if len(page.getText()) > 0:
        return False
    # 要求页面中不能包含大于 1 张插图（防止碎图情况）
    if len(page.get_images()) > 1:
        return False

    return True

def pdf_to_images(pdf_path):
    # 打开 PDF 文件
    doc = fitz.open(pdf_path)

    images = []
    for pno in range(doc.pageCount):
        # print(f'\n[INFO] {pdf_path} \n    Page: {pno}')
        page = doc.loadPage(pno)
        print(f'[INFO] {page}')

        encoded_images = []
        if image_in_page(page) == True:
            blocks = page.getText("dict")["blocks"]  # the list of block dictionaries
            imgblocks = [b for b in blocks if b["type"] == 1]
            for imgblock in imgblocks:
                contents = imgblock['image']
                encoded_images.append(contents)
        else:
            # print(page.rotation)
            mat = fitz.Matrix(2., 2.)
            pix = page.getPixmap(matrix=mat)
            contents = pix.tobytes(output="png")
            # contents = pix.pil_tobytes(format="PNG", optimize=True)
            encoded_images.append(contents)

        for index, contents in enumerate(encoded_images):
            # 借助 TensorFlow API 把图从二进制编码读起来，支持四种格式 BMP, GIF, JPEG, or PNG
            img = tf.io.decode_image(contents, channels=3)
            images.append(img.numpy())
    return images


if __name__ == "__main__":

    images = pdf_to_images('/home/lk/MyProject/BMW/客户测试问题分析/1216/流水验真测试问题/建行假判断为真.pdf')

    for image in images:
        print(image.shape)
        # plt.imshow(image)
        # plt.show()