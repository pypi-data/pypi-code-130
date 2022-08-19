# -*- coding: utf-8 -*-
import os

import hao
import jieba
import regex
from tailors.utils import locations

from . import stopwords, texts

LOGGER = hao.logs.get_logger(__name__)

PUNCTUATIONS_EN = r'!"#$%&\'()*+,-./:;<=>?@[]^_`{|}~'
PUNCTUATIONS_ZH = r'＂＃＄￥％＆＇（）＊＋，－／：；＜＝＞＠［］＾＿｀｛｜｝～｟｠｢｣､\u3000、〃〈〉《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏﹑﹔·！？｡。'
PUNCTUATIONS_SPECIAL = '°∠г₂₂³×ɡΦΦφφФ′′ⅠⅣⅣ→≤≤≥≦°□こ'
PUNCTUATIONS = f'{PUNCTUATIONS_EN}{PUNCTUATIONS_ZH}{PUNCTUATIONS_SPECIAL}'


P_CITIES = hao.regexes.re_compile([c.strip('省市县镇村区') for c in locations.get_provinces_and_cities()])


P_NEG = hao.regexes.re_compile([
    rf'[{regex.escape(PUNCTUATIONS)}]',
    r'[一二三四五六七八九十百千万0-9]',
    r'[a-z]',
    r'^[A-Z]{,2}$',
    r'[一二三四五六七八九十百千万0-9]+[段届标期次批名个道封颗堵台首张根扇顶盘条幅件株位朵间头则片支峰篇只棵块粒匹座面方栋把枚斤批车平份人]',
    r'[ⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹⅠⅡⅢⅣⅤⅥⅦⅧⅨХⅩⅪⅫ①②③④⑤⑥⑦⑧⑨⑩⒈⒉⒊⒋⒌⒍⒎⒏⒐⒑⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩ⓐⓑⓒⓓⓔⓕⓖ]',
    r'[ΑαΒβΓγΔδΕεΖζΗηΘθΙιΚκΛλΜμΝνΞξΟοΠπΡρΣσΤτΥυΦφΧχΨψΩω]',
    r'[①-⑯⓵-⓾⒈-⒛➀-➉⑪-⑳⓿❶-❿➊-➓⓫-⓴⑴-⒇]',
    r'[_ᅳ]',
    r'[À-ÿ]',
    r'[〇ㄉㄊ㘵㳇至]',
    r'[段路村镇岭区街道寺线寨河海湖渡行庄府山桥港铺水]$',
    r'政采',
])


class AbstractTokenizer(object):

    def __init__(self) -> None:
        super().__init__()

    def tokenize(self, text):
        text = self.pre_tokenize(text)
        return self.cut(text)

    def pre_tokenize(self, text):
        return texts.fix_text(text)

    def cut(self, text):
        raise NotImplementedError()


class JiebaTokenizer(AbstractTokenizer):

    def __init__(self,
                 min_size: int = 1,
                 stopwords_path = 'data/dict/stopwords.txt',
                 keywords_path = 'data/dict/keywords.txt') -> None:
        super().__init__()
        self._min_size = min_size
        self._stopwords = stopwords.get_stopwords(stopwords_path)
        self._tokenizer = self._init_tokenizer(keywords_path)

    def _init_tokenizer(self, keywords_path):
        hao.paths.set_temp_dir('~/.tmp')
        tokenizer = jieba.Tokenizer()

        file_path = hao.path.get(keywords_path)
        if os.path.exists(file_path):
            with open(file_path) as f:
                for line in f:
                    line = hao.strings.strip_to_none(line)
                    if line is not None:
                        tokenizer.add_word(line)
        else:
            LOGGER.warning(f"keywords file not found: {keywords_path}")
        tokenizer.initialize()
        return tokenizer

    def cut(self, text):
        items = []
        for word in self._tokenizer.lcut(text):
            if len(items) > 0 and word == ' ' == items[-1]:
                continue
            if not self.is_valid_word(word):
                continue
            items.append(word.replace("\r", "").replace("\n", ""))
        return items

    def cut_and_join(self, text, sep=' '):
        return sep.join(self.cut(text))

    def is_valid_word(self, word):
        len_word = len(word)
        if self._min_size > 1 and len_word < self._min_size:
            return False
        if len_word == 1 and not hao.strings.is_char_chinese(word):
            return False
        if P_NEG.search(word) is not None:
            return False
        if word in self._stopwords:
            return False
        if P_CITIES.search(word) is not None:
            return False
        return True


class CharTokenizer(AbstractTokenizer):

    def cut(self, text):
        return list(text)
