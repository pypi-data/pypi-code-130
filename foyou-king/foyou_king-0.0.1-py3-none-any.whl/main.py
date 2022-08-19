from typing import Tuple

import fire
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from king import __version__, King
from king.yinxiao import YinXiao

urllib3.disable_warnings(InsecureRequestWarning)


class CLI:

    @staticmethod
    def search(q: str, p=1, pn=10):
        """搜索铃声

        q: 关键词
        p: 页码
        pn: 分页大小（获取多少条）
        """
        king = King()
        rings = king.all_search(q, p=p, pn=pn)
        print('{:2}{:^8}{:2}{:10}{:20}{}'.format('', '持续时间', '', '铃声名称', '', '下载地址'))
        for index, ring in enumerate(rings):
            ring_name = ring.ringName
            if len(ring_name) > 20:
                ring_name = ring_name[:11] + '...'
            print('{:>2}{:<2}{:^8}{:2}{:<20}{:4}{}'.format(index, '.', ring.duration, '', ring_name, '', ring.url))

    @staticmethod
    def tips(q: str, pn=10):
        """搜索词推荐

        q: 关键词
        pn: 分页大小（获取多少条）
        """
        king = King()
        print('{:^10}{:8}{:<30}'.format('热度', '', '搜索词'))
        for tip in king.get_tip_list(q, pn):
            print('{:>8}{:8}{:<30}'.format(tip.Hot, '', tip.HintInfo))

    @staticmethod
    def down(q: str, p=1, pn=10, n: Tuple[int] = None, d='.'):
        """下载铃声

        q: 关键词
        p: 页码
        pn: 分页大小（获取多少条）
        n: 需要下载的序号，-n 1 或者 -n 2,5,7
        d: 下载目录
        """
        king = King(d)
        rings = king.all_search(q, p=p, pn=pn)
        if n is None:
            for ring in rings:
                king.download_ring(ring.ringName, ring.url)
        else:
            if isinstance(n, int):
                n = (n,)
            for i in n:
                ring = rings[int(i)]
                king.download_ring(ring.ringName, ring.url)

    @staticmethod
    def version():
        """显示版本"""
        print('king version', __version__)


class YinXiaoCLI:
    @staticmethod
    def version():
        """显示版本"""
        print('version', __version__)

    @staticmethod
    def search(q: str, p=1, b=False, kind: bool = False, tag: bool = False):
        """搜索音效

        q: 关键词
        p：页码
        kind: 分类，比如 "-kind sajiao"
        tag: 标签，比如 "-tag qingxu"
        """
        yx = YinXiao()
        total = None
        if kind:
            rings = yx.kind(q, p=p, b=b)
        elif tag:
            rings = yx.tag(q, p=p, b=b)
        else:
            total, rings = yx.search(q, p=p, b=b)

        if total:
            header = f'共搜索到 {total} 条 "{q}" 音效，第 {p} 页，当前页 {len(rings)} 条'
            print(header)
            print('-' * len(header))
        elif rings is None:
            print(f'tag/king "{q}" 不存在')
            return

        print('{:2}{:^8}{:2}{:10}{:20}{}'.format('', '持续时间', '', '铃声名称', '', '下载地址'))
        for index, audio in enumerate(rings):
            ring_name = audio.name
            if len(ring_name) > 20:
                ring_name = ring_name[:11] + '...'
            print('{:>2}{:<2}{:^8}{:2}{:<20}{:4}{}'.format(index, '.', audio.duration, '', ring_name, '', audio.url))

    @staticmethod
    def down(q: str, p=1, b=False, n: Tuple[int] = None, d='.', kind: bool = False, tag: bool = False):
        """下载音效

        q: 关键词
        p：页码
        b: 商用
        d: 下载目录
        n: 下载哪些，比如 "-n 1" / "-n 1,2,6"
        kind: 分类，比如 "-kind sajiao"
        tag: 标签，比如 "-tag qingxu"
        """
        yx = YinXiao(d)
        total = None
        if kind:
            rings = yx.kind(q, p=p, b=b)
        elif tag:
            rings = yx.tag(q, p=p, b=b)
        else:
            total, rings = yx.search(q, p=p, b=b)

        if total is None and rings is None:
            print(f'tag/king "{q}" 不存在')
            return

        if n is None:
            for audio in rings:
                yx.download_ring(audio.name, audio.url)
        else:
            if isinstance(n, int):
                n = (n,)
            for i in n:
                audio = rings[int(i)]
                yx.download_ring(audio.name, audio.url)


def main():
    fire.Fire(CLI)


def yxiao():
    fire.Fire(YinXiaoCLI)


if __name__ == '__main__':
    main()
