# -*- coding: utf-8 -*-
import hao

LOGGER = hao.logs.get_logger(__name__)

NUMBER_MAPPING = {
    '0': '零',
    '1': '一',
    '2': '二',
    '3': '三',
    '4': '四',
    '5': '五',
    '6': '六',
    '7': '七',
    '8': '八',
    '9': '九',
}


def generate_chinese_year_ranges(start=1950, end=2050):
    years = list()
    for year in range(start, end):
        year = str(year)
        chinese_year = list()
        for ch in year:
            chinese_year.append(NUMBER_MAPPING.get(ch, ch))
        years.append(''.join(chinese_year) + '年')
    return years
