# -*- coding: utf-8 -*- 
# Time: 2022-03-01 11:00
# Copyright (c) 2022
# author: Euraxluo

import copy
import asyncio
import warnings

import polyline
from concurrent import futures
from amap_distance_matrix.helper import *
from amap_distance_matrix.services.register import register

"""
Osrm webapi接口服务包装
"""


###############osrm################


def osrm_distance(origin: list, destination: list):
    """
    osrm 距离
    :param origin:[float,float]
    :param destination:[float,float]
    :return:
    """
    data = futures_osrm([origin, destination], service="route")
    return data['routes'][0]['distance']


def request_osrm(url, idx, data_list):
    """
    通过导航url获取导航数据并进行结果设置
    :param url: 导航url
    :param idx: 结果集合索引
    :param data_list:
    :return:
    """
    try:
        data = register.session().get(url).json()
        data_list[idx] = data
    except Exception as e:
        register.logger.warning(f"Osrm Error:{e},url:{url}")


def futures_osrm(urls: list) -> dict:
    """
    异步 基于 osrm url list 通过请求接口 获得 路径规划结果
    :param urls:
    :return:
    """
    data_collections = [None] * len(urls)
    pack_data_result = {}
    all_tasks = []
    # 准备
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        try:
            event_loop = asyncio.get_event_loop()
        except Exception as _:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            event_loop = asyncio.get_event_loop()
    # 添加task
    for idx in range(len(urls)):
        all_tasks.append(event_loop.run_in_executor(register.pool, request_osrm, urls[idx], idx, data_collections))
    # 运行
    event_loop.run_until_complete(asyncio.wait(all_tasks))

    service = urls[0].split('/')[3] + 's'

    for idx in range(len(urls)):
        api_data_result = data_collections[idx]
        if not api_data_result:
            request_osrm(urls[idx], idx, data_collections)

        if not pack_data_result:
            pack_data_result = api_data_result
            pack_data_result['strategy'] = service
            pack_data_result['total_duration'] = api_data_result[service][0]['duration']
            pack_data_result['total_distance'] = api_data_result[service][0]['distance']
            pack_data_result['steps'] = []
            loc_list: List[float] = polyline.decode(api_data_result[service][0]['geometry'])  # [(lat,lon)]
            waypoint_locations = [waypoint['location'] for waypoint in api_data_result['waypoints']]
            steps = [(i['distance'], i['duration'], i['weight']) for i in api_data_result[service][0]['legs']]
            for step_idx, (b, e) in enumerate(zip(waypoint_locations, waypoint_locations[1:])):
                b_geohash = geo_encode(*b)
                e_geohash = geo_encode(*e)
                polyline_point_list = []
                begin = False
                tmp_loc_list = copy.deepcopy(loc_list)
                precision = 8
                while not begin and precision > 6:
                    for loc_idx, i in enumerate(tmp_loc_list):
                        poly_geohash = geo_encode(i[1], i[0], precision=precision)
                        if poly_geohash == b_geohash:
                            begin = True
                        if poly_geohash == e_geohash:
                            polyline_point_list.append((i[1], i[0]))
                            loc_list = loc_list[loc_idx:]
                            break
                        if begin:
                            polyline_point_list.append((i[1], i[0]))
                    else:
                        precision -= 1
                        continue
                    break
                pack_data_result['steps'].append({
                    "distance": steps[step_idx][0],
                    "duration": steps[step_idx][1],
                    "polyline": loc_to_str(polyline_point_list),
                    "tmc": steps[step_idx][2],
                    "origin": b,
                    "destination": e,
                })

            pack_data_result['origin'] = waypoint_locations[0]
            pack_data_result['destination'] = waypoint_locations[-1]
        else:
            pack_data_result['total_duration'] += api_data_result[service][0]['duration']
            pack_data_result['total_distance'] += api_data_result[service][0]['distance']
            waypoint_locations = [waypoint['location'] for waypoint in api_data_result['waypoints']]
            pack_data_result['destination'] = waypoint_locations[-1]

            loc_list: List[float] = polyline.decode(api_data_result[service][0]['geometry'])  # [(lat,lon)]
            steps = [(i['distance'], i['duration'], i['weight']) for i in api_data_result[service][0]['legs']]
            for step_idx, (b, e) in enumerate(zip(waypoint_locations, waypoint_locations[1:])):
                b_geohash = geo_encode(*b)
                e_geohash = geo_encode(*e)
                polyline_point_list = []
                begin = False
                tmp_loc_list = copy.deepcopy(loc_list)
                precision = 8
                while not begin:
                    for loc_idx, i in enumerate(tmp_loc_list):
                        poly_geohash = geo_encode(i[1], i[0], precision=precision)
                        if poly_geohash == b_geohash:
                            begin = True
                        if poly_geohash == e_geohash:
                            polyline_point_list.append((i[1], i[0]))
                            loc_list = loc_list[loc_idx:]
                            break
                        if begin:
                            polyline_point_list.append((i[1], i[0]))
                    precision -= 1
                pack_data_result['steps'].append({
                    "distance": steps[step_idx][0],
                    "duration": steps[step_idx][1],
                    "polyline": loc_to_str(polyline_point_list),
                    "tmc": steps[step_idx][2],
                    "origin": b,
                    "destination": e,
                })
    del pack_data_result['code']
    del pack_data_result[service]
    del pack_data_result['waypoints']
    return pack_data_result


def osrm_url(origin: list, destination: list, waypoints: list = None, service: str = 'route', profile: str = 'car', version: str = 'v1',
             batch_size: int = 100, host: str = None) -> list:
    """
    将数据包装为 osrm_url urls
    所有经纬度应该使用wgs火星坐标
    :param origin:
    :param destination:
    :param waypoints:
    :param service:
    :param version:
    :param profile:
    :param batch_size:
    :param host:
    :return:
    """
    if waypoints is None:
        waypoints = []
    if host is None:
        host = register.osrm_host
    loc_list = [origin] + waypoints + [destination]
    urls = []
    for idx in [(i, i + batch_size) for i in range(0, len(loc_list), batch_size)]:
        tmp_points = loc_list[idx[0] - 1 if idx[0] > 1 else 0:idx[1]]
        urls.append(f"{host}/{service}/{version}/{profile}/{loc_to_str(tmp_points)}")
    return urls


def osrm_batch(origin: list, destination: list, waypoints: list = None, profile="car", version="v1", batch_size=100, host: str = None):
    """
    所有经纬度应该使用wgs火星坐标
    异步进行osrm url的构建,以及请求
    :param origin:
    :param destination:
    :param waypoints:
    :param service:
    :param profile:
    :param version:
    :param batch_size:
    :param host:
    :return:
    """
    if host is None:
        host = register.osrm_host
    service = "route"  # 一定是route
    urls = osrm_url(origin=origin, destination=destination, waypoints=waypoints, service=service, profile=profile, version=version, batch_size=batch_size, host=host)
    data = futures_osrm(urls=urls)
    if data['total_distance'] == 0 and geohash.encode(longitude=origin[0], latitude=origin[1], precision=8) != geohash.encode(longitude=destination[0], latitude=destination[1], precision=8):
        raise ValueError("Osrm Data Abort!")
    return data
