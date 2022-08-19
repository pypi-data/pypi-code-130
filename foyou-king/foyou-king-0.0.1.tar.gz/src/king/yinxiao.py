"""
设计一下：

yxiao search <关键词> -p <页码>
yxiao down <关键词> -p <页码> -n 1,2,3
yxiao kind piantouyinxiao -p <页码>
"""
from dataclasses import dataclass
from typing import Tuple, List, Optional

import requests
from parsel import Selector

from king.Downloader import Downloader


@dataclass
class Audio:
    name: str = None
    duration: str = None
    url: str = None


class YinXiao:

    def __init__(self, download_folder='.', proxies: dict = None):
        self._downloader = Downloader(download_folder)
        session = requests.session()
        session.trust_env = False
        session.proxies = proxies
        session.headers[
            'user-agent'] = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/103.0.0.0 Safari/537.36')
        self.session = session

    @staticmethod
    def get_ok_url(url: str):
        if url.startswith('//'):
            return f'https:{url}'
        return url

    def search(self, q: str, p=1, b=False) -> Tuple[int, List[Audio]]:
        """
        q: 关键词
        p: 页码，页码大小不支持
        b：商用音效
        """
        resp = self.session.get(
            'https://sc.chinaz.com/yinxiao/index'
            f"{'' if p == 1 else '_' + str(p)}.html?{'business=1&' if b else ''}keyword={q}")
        html = Selector(resp.text)
        # 总条数
        total = html.css('#Search-Tip > div > p > span::text')[0]
        total = int(total.get().strip())
        element_list = html.css('#AudioList .audio-item')
        audio_list = []
        for element in element_list:
            duration = element.css('div.audio-time > p::text').get()
            name = element.css('.name::text').get().strip()
            url = element.css('audio[src]').attrib['src']
            url = self.get_ok_url(url)
            audio_list.append(Audio(name=name, duration=duration, url=url))

        return total, audio_list

    def kind(self, q: str, p=1, b=False) -> Optional[List[Audio]]:
        """
        q: 分类，情绪 -> qingxu
        p: 页码，页码大小不支持
        b：商用音效
        """
        resp = self.session.get(
            'https://sc.chinaz.com/yinxiao/'
            f"{q}{'' if p == 1 else '_' + str(p)}.html?{'business=1&' if b else ''}")
        if resp.url.endswith('404.html'):
            return None
        html = Selector(resp.text)
        element_list = html.css('#AudioList .audio-item')
        audio_list = []
        for element in element_list:
            duration = element.css('div.audio-time > p::text').get()
            name = element.css('.name::text').get().strip()
            url = element.css('audio[src]').attrib['src']
            url = self.get_ok_url(url)
            audio_list.append(Audio(name=name, duration=duration, url=url))

        return audio_list

    def tag(self, q: str, p=1, b=False) -> Optional[List[Audio]]:
        """
        q: 标签，比如 可爱 -> keai
        p: 页码，页码大小不支持
        b：商用音效
        """
        resp = self.session.get(
            'https://sc.chinaz.com/tag_yinxiao/'
            f"{q}{'' if p == 1 else '_' + str(p)}.html{'?business=1&' if b else ''}")
        if resp.url.endswith('404.html'):
            return None
        html = Selector(resp.content.decode())
        element_list = html.css('.audio-list .audio-item')
        audio_list = []
        for element in element_list:
            duration = element.css('div.audio-time > p::text').get()
            name = element.css('.name::text').get().strip()
            url = element.css('audio[src]').attrib['src']
            url = self.get_ok_url(url)
            audio_list.append(Audio(name=name, duration=duration, url=url))

        return audio_list

    def download_ring(self, ring_name: str, ring_url: str):
        *_, ring_suffix = ring_url.split('?')[0].split('.')
        return self._downloader.download(ring_url, f"{ring_name.strip('。，,. ')}.{ring_suffix}")
