# -*- coding: utf-8 -*-
import ftfy
import hao
import opencc
import regex

CC = opencc.OpenCC('t2s')

P_DATES = hao.regexes.re_compile([
    r'(?:一九|二零|二〇|二O|二0)[O0零〇一二三四五六七八九]{2}\s*年\s*十?[一二三四五六七八九十]\s*月\s*(?:(?:十|二十|三十)?[一二三四五六七八九十]?\s*日)?份?',
    r'\d{4}\s*\D\s*\d{1,2}\s*\D\s*\d{1,2}\s*\D{,2}\s*(?:\d{1,2}\s*\D\d{1,2}\s*\D\s*(?:\d{1,2})?)?',
])
P_NORMALIZE = (
    (P_DATES, ''),
    (regex.compile(r'(?<=\b[\u4e00-\u9fa5])\s*(?=[\u4e00-\u9fa5]\b)'), ''),
    (regex.compile(r'[∆|\s]+'), ' '),
)

P_INVALID_TEXT = hao.regexes.re_compile([
    r'[锟铰斤揭艿拷]{3,}',
])


def is_invalid_text(text: str) -> bool:
    if text is None:
        return True
    if hao.strings.is_invalid_chinese(text):
        return True
    if P_INVALID_TEXT.search(text) is not None:
        return True
    return False


def fix_text(text):
    if text is None:
        return ''
    text = fix_linebreaks(text)
    text = ftfy.fix_text(text)
    text = traditional_to_simplified(text)
    for p, sub in P_NORMALIZE:
        text = p.sub(sub, text)
    return text


def fix_linebreaks(text):
    text = regex.sub(r'([。！？\?])([^”’])', r"\1\n\2", text)  # 单字符断句符
    text = regex.sub(r'(\.{6})([^”’])', r"\1\n\2", text)  # 英文省略号
    text = regex.sub(r'(\…{2})([^”’])', r"\1\n\2", text)  # 中文省略号
    text = regex.sub(r'([。！？\?][”’])([^，。！？\?])', r'\1\n\2', text)
    return text.rstrip()


def traditional_to_simplified(text):
    converted = CC.convert(text)
    if len(set(converted) - set(text)) >= 10:
        return converted
    return text
