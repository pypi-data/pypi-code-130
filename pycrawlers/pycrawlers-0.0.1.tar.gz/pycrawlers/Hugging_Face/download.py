# -*- coding: UTF-8 -*-
# @Time : 2022/8/17 15:38 
# @Author : 刘洪波

"""
获取hugging face 模型
"""
import time
from pycrawlers.common.default_data import headers
from pycrawlers.common.tools import crawl_html
from pycrawlers.common.tools import download
from pycrawlers.common.tools import juedge_path
from pycrawlers.common.tools import juedge_url


class HuggingFace(object):
    def __init__(self, base_url: str = None):
        self.base_url = base_url if base_url else 'https://huggingface.co'
        self.tag = True if base_url else False
        self.html_data = None

    def get_data(self, url: str, file_save_path: str = None):
        """
        获取单个数据
        :param url: 例：'htt://huggingface.co/albert-base-v2/tree/main'
        :param file_save_path: None or './albert-base-v2'
        :return:
        """
        juedge_url(url)
        _url = url.split('/')
        if not self.tag:
            self.get_base_url(_url)
        self.html_data = crawl_html(url, headers)
        file_names = self.get_file_names()
        file_urls = self.get_file_urls()
        files_path = juedge_path(file_save_path) if file_save_path else juedge_path('./' + _url[-3] + '/')
        print(f"{'$' * 30}{' ' * 5}开始下载：{_url[-3]}{' ' * 5}{'$' * 30}")
        self.get_files(file_names, file_urls, files_path)
        print(f"{'$' * 30}{' ' * 5}完成下载{' ' * 5}{'$' * 30}")

    def get_batch_data(self, urls: list, file_save_paths: list = None):
        """
        批量获取数据
        :param urls: ['https://huggingface.co/albert-base-v2/tree/main', 'https://huggingface.co/dmis-lab/biosyn-sapbert-bc5cdr-disease/tree/main']
        :param file_save_paths:['./model_1/albert-base-v2', './model_2/']
        :return:
        """
        success_urls = []
        fail_urls = []
        if file_save_paths:
            if len(urls) == len(file_save_paths):
                for u, f in zip(urls, file_save_paths):
                    success_urls, fail_urls = self.fault_tolerant(u, success_urls, fail_urls, f)
            else:
                raise ValueError('The number of urls and paths is inconsistent')
        else:
            for url in urls:
                success_urls, fail_urls = self.fault_tolerant(url, success_urls, fail_urls)

    def fault_tolerant(self, url: str, success_urls: list, fail_urls: list, path: str = None):
        """容错处理"""
        try:
            self.get_data(url, path)
            success_urls.append(url)
            time.sleep(0.5)
        except Exception as e:
            print(e)
            fail_urls.append(url)
        return success_urls, fail_urls

    def get_base_url(self, _url: list):
        """获取基础url"""
        if len(_url) > 5:
            if 'http' in _url[0] and _url[1] == '':
                self.base_url = _url[0] + '//' + _url[2]

    def get_file_names(self):
        """获取文件名"""
        xpath = f'//section/ul/li/a[1]/span[1]/text()'
        return self.html_data.xpath(xpath)

    def get_file_urls(self):
        """获取文件链接"""
        xpath = f'//section/ul/li/a[2]/@href'
        return self.html_data.xpath(xpath)

    @staticmethod
    def generate_file_path(_url: list):
        """生成路径"""
        return juedge_path('./' + _url[-3] + '/')

    def get_files(self, file_names, file_urls, files_path):
        for name, part_url in zip(file_names, file_urls):
            if name in part_url:
                url = self.base_url + part_url
                download(url, files_path + name, headers)

    @staticmethod
    def count_info(success_urls, fail_urls):
        print(f'程序执行统计：\n')
        print(f'a. 成功{str(len(success_urls))}个\n')
        print(f'b. 失败{str(len(fail_urls))}个\n')
        print(f'c. 成功的URL：{"，".join(success_urls)}')
        print(f'd. 失败的URL：{"，".join(fail_urls)}')
