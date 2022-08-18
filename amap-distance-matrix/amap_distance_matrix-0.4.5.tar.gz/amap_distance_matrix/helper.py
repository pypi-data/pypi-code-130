# -*- coding: utf-8 -*- 
# Time: 2022-03-01 11:01
# Copyright (c) 2022
# author: Euraxluo


import time
import datetime
import itertools
import functools
import geohash
from math import radians, cos, sin, asin, sqrt
from typing import *


def check_location(location: List[float]) -> bool:
    if not location and len(location) < 2:
        return False
    if 73 < location[0] < 136 and 3 < location[1] < 54:
        return True
    return False


def loc_to_str(loc_list: list, revers: bool = False) -> str:
    """
    坐标列表转字符串
    :param loc_list:[[float,float]]
    :param revers:False,是否翻转坐标 xy=>yx
    :return:str:'float,float'
    """
    if revers:
        loc_s_list = [str(loc[1]) + "," + str(loc[0]) for loc in loc_list]
    else:
        loc_s_list = [str(loc[0]) + "," + str(loc[1]) for loc in loc_list]
    loc_str = loc_s_list[0]
    for loc_s in loc_s_list[1:]:
        loc_str += ";" + loc_s
    return loc_str


def format_loc(loc_str: str, revers=False) -> list:
    """
    坐标字符串转换
    :param loc_str: str:'float,float'
    :param revers:False
    :return:[float,float]
    """
    if revers:
        return [float(i) for i in loc_str.split(',')[::-1]]
    return [float(i) for i in loc_str.split(',')[::]]


def wgs2gcj(Lon: float, Lat: float) -> Tuple[float]:
    from coord_convert.transform import wgs2gcj
    return wgs2gcj(wgsLon=Lon, wgsLat=Lat)


def gcj2wgs(Lon: float, Lat: float) -> Tuple[float]:
    from coord_convert.transform import gcj2wgs
    return gcj2wgs(gcjLon=Lon, gcjLat=Lat)


def haversine(loc1, loc2):
    """
    经纬度距离
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [loc1[0], loc1[1], loc2[0], loc2[1]])
    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # 地球平均半径，单位为公里
    return c * r * 1000


def time_slot_wmh(date_time: datetime.datetime = None):
    """
    时间段
    :param date_time:
    :return: w0m0h
    """
    if date_time is None:
        date_time = datetime.datetime.now()
    weekday = str(date_time.weekday() + 1)
    month = '0' + str(date_time.month) if date_time.month < 10 else str(date_time.month)
    hour = '0' + str(date_time.hour) if date_time.hour < 10 else str(date_time.hour)
    return weekday + month + hour


def geo_encode(lon: float, lat: float, precision=8):
    return geohash.encode(longitude=lon, latitude=lat, precision=8)


def geo_decode(hashcode: str):
    return geohash.decode(hashcode)


def distinct_point(*points: Union[List[float], Tuple[float]]) -> Tuple[Tuple[float]]:
    # 1.去重
    distinct_point_list: List[Tuple[float]] = []

    for point in points:
        if isinstance(point, list):
            point = tuple(point)
        if point not in distinct_point_list:
            distinct_point_list.append(point)
    distinct_point_list.sort(key=lambda x: str(x[0]) + '_' + str(x[-1]))
    return tuple(distinct_point_list)


def ignore_unhashable(func):
    uncached = func.__wrapped__
    attributes = functools.WRAPPER_ASSIGNMENTS + ('cache_info', 'cache_clear')

    @functools.wraps(func, assigned=attributes)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError as error:
            if 'unhashable type' in str(error):
                return uncached(*args, **kwargs)
            raise

    wrapper.__uncached__ = uncached
    return wrapper


# @ignore_unhashable
# @functools.lru_cache()
def points_permutations_sorted(distinct_point_list: Tuple[Tuple[float]]) -> Tuple[Tuple[Tuple[float]]]:
    # 2. 获取全排列数据
    adjacency_list: Dict[Tuple[float], Set[Tuple[float]]] = {}
    all_edges = set()
    for edge in itertools.permutations(distinct_point_list, 2):
        if edge[0] not in adjacency_list:
            adjacency_list[edge[0]] = set()
        adjacency_list[edge[0]].add(edge[1])
        all_edges.add(edge)
    # 3.collection
    sorted_edge: List[Tuple[Tuple[float], ...]] = []
    while len(all_edges) > 0:
        if not sorted_edge or sorted_edge[-1][-1] not in adjacency_list:
            # 如果结果集合为空,则随便取一个数据
            edge = all_edges.pop()
            start_node = edge[0]
            if sorted_edge and sorted_edge[-1][-1]:
                sorted_edge.append((sorted_edge[-1][-1], start_node))
            # 从邻接表中移除一个边
            adjacency_list[edge[0]].remove(edge[1])
        else:
            # 获取排序边集合的最后一个元素的终点,作为起点
            start_node = sorted_edge[-1][-1]
            # 据此起点,从邻接表中获取并弹出end_node
            end_node = adjacency_list[start_node].pop()
            edge = (start_node, end_node)
            # 将该边从所有集合中去掉
            all_edges.remove(edge)
        if len(adjacency_list[start_node]) == 0:
            del adjacency_list[start_node]
        sorted_edge.append(edge)
    return tuple(sorted_edge)


def point_pairing_sorted(*points: Union[List[float], Tuple[float]]) -> Tuple[Tuple[Tuple[float], ...]]:
    """
    通过点的全排列,得到待排序的点对
    通过分配收集算法,将点对排序
    :param points:待排列的点序列
    :return:
    """
    distinct_point_list = distinct_point(*points)
    return points_permutations_sorted(distinct_point_list)
