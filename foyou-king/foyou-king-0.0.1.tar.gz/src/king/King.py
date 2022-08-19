from typing import List

import requests

from .CompleteSearchResponse import CompleteSearchResponse
from .Config import *
from .Downloader import Downloader
from .MusicInfo import MusicInfo
from .TipResponse import TipResponse


# noinspection SpellCheckingInspection
class King:
    """酷狗铃声"""

    def __init__(self, download_folder='.', proxies: dict = None):
        self._downloader = Downloader(download_folder)
        session = requests.session()
        session.trust_env = False
        session.proxies = proxies
        session.headers['user-agent'] = 'Android12-Phone-201-0-FANet-wifi'
        session.headers['authorization'] = 'OEPAUTH realm="OEP",netMode="WIFI",version="S1.0"'
        session.headers['x-api-id'] = 'android/5.9.3/25m/release'
        session.headers['x-device-id'] = '3672ce37818443aba3543468a67c990a'
        self.session = session

    def get_tip_list(self, key: str, amount: int = 10) -> List[TipResponse]:
        """获取搜索词建议

        :param key: 搜索词
        :param amount: 条数
        :return:
        """
        response = self.session.get(HTTP_API_HOST + RING_SEARCH_TIP, params={
            'key': key,
            'amount': amount
        })
        return [TipResponse.fill_dataclass(item) for item in response.json()['response']['list']]

    def search(self, q: str, p=1, pn=20, st=1, t=3, subtype=1, plat=3) -> List[MusicInfo]:
        """搜索铃声

        :param q: 搜索词
        :param p: 页码
        :param pn: 分页大小
        :param st: 铃声类型
            1. 彩铃
            2. 非 DIY 铃声
            3. DIY 铃声
        :param t: 类型，
        :param subtype: 子类型，具体含义未知
        :param plat: 平台
        :return:
        """
        response = self.session.get(HTTP_API_HOST + RING_SEARCH, params={
            'q': q,
            't': t,
            'subtype': subtype,
            'p': p,
            'pn': pn,
            'st': st,
            'plat': plat
        })
        return [MusicInfo.fill_dataclass(item) for item in response.json()['response']['musicInfo']]

    def complex_search(self, q: str, phone_type=3, plat=3) -> CompleteSearchResponse:
        """综合搜索

        :param q: 关键词
        :param phone_type: 运营商，可选值 [1, 2, 3]
        # phone_types: {
        # 	"1": ["134", "135", "136", "137", "138", "139", "144", "147", "148", "150", "151", "152", "157", "158",
                                        "159", "172", "178", "182", "183", "184", "187", "188", "195", "197", "198"],
        # 	"2": ["130", "131", "132", "145", "146", "155", "156", "166", "171", "175", "176", "185", "186", "196"],
        # 	"3": ["133", "149", "153", "162", "170", "173", "177", "180", "181", "189", "190", "191", "193", "199"],
        # }
        :param plat: 平台
        :return:
        """
        response = self.session.get(HTTP_API_HOST + RING_COMPLEX_SEARCH, params={
            'q': q,
            'phone_type': phone_type,
            'plat': plat
        })
        return CompleteSearchResponse.fill_dataclass(response.json()['response'])

    def all_search(self, q: str, p=1, pn=30, t=3, subtype=1, plat=3) -> List[MusicInfo]:
        """铃声搜索（DIY + 非DIY）

        :param q: 关键词
        :param p: 页码
        :param pn: 分页大小
        :param t: 未发现其他可选值
        :param subtype: 未发现其他可选值
        :param plat: 平台，具体作用未知
        :return:
        """
        response = self.session.get(HTTP_API_HOST + RING_ALL_SEARCH, params={
            'q': q,
            't': t,
            'subtype': subtype,
            'p': p,
            'pn': pn,
            'plat': plat
        })
        return [MusicInfo.fill_dataclass(item) for item in response.json()['response']['musicInfo']]

    def tracker(self, ring_id: int):
        raise NotImplementedError('缺少签名算法，暂未实现')
        # response = self.session.get(HTTP_API_HOST + RING_TRACKER, params={
        #     'ringId': '',
        #     'dateline': '',
        #     'token': ''
        # })

    def circle_hot_list(self):
        raise NotImplementedError('缺少签名算法，暂未实现')
        # response = self.session.get(HTTP_API_HOST + CIRCLE_HOT_LIST, params={
        #     'dateline': '',
        #     'token': ''
        # })

    def download_ring(self, ring_name: str, ring_url: str):
        *_, ring_suffix = ring_url.split('?')[0].split('.')
        return self._downloader.download(ring_url, f"{ring_name.strip('。，,. ')}.{ring_suffix}")
