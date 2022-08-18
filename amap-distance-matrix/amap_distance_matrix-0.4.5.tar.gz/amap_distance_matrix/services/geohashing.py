# -*- coding: utf-8 -*- 
# Time: 2022-03-02 15:13
# Copyright (c) 2022
# author: Euraxluo


from amap_distance_matrix.helper import *
from amap_distance_matrix.services.register import register


def geo_add(*points: List[float], key: str = ""):
    """
    添加 经纬度并转为geohash
    :param key:
    :param points:
    :return:
    """
    if not key:
        key = register.geo_key
    values = []
    [values.extend([point[0], point[1], geo_encode(*point)]) for point in points]
    register.redis.execute_command('GEOADD', key, *values)


def geo_radius(point: List[float], dist: int = 200, unit: str = 'm', key: str = ""):
    """
    根据经纬度,返回 缓存的 数据
    :param key: 存储key
    :param point: 经纬度
    :param dist: 距离
    :param unit: 单位
    :return:
    """
    if not key:
        key = register.geo_key
    radius = register.redis.georadius(key, point[0], point[1], dist, unit, withdist=True, withcoord=True, sort='ASC')
    result_list = []
    for resp in radius:
        result = {
            'name': '',
            'distance': 0,
            'lon': 0,
            'lat': 0,
        }
        if resp:
            if isinstance(resp[0], bytes):
                result['name'] = str(resp[0], encoding='utf8')
            else:
                result['name'] = str(resp[0])
            result['distance'] = resp[1]
            result['lon'] = resp[2][0]
            result['lat'] = resp[2][1]
        result_list.append(result)
    return result_list
