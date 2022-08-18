# -*- coding: utf-8 -*- 
# Time: 2022-03-01 11:00
# Copyright (c) 2022
# author: Euraxluo

import traceback
import aiohttp
import random
import asyncio
import warnings
from concurrent import futures
from amap_distance_matrix.helper import *
from amap_distance_matrix.schemas.amap import *
from amap_distance_matrix.services.register import register

"""
高德地图webapi接口服务包装
"""


###############navigating################

def navigating_url(origin: list, destination: list, waypoints: list = None,
                   batch_size: int = 12, strategy: int = 1, output: str = "json",
                   keys: Union[str, list] = None, host: str = "https://restapi.amap.com/v3/direction/driving") -> list:
    """
    将waypoints包装为driving_url urls
    :param host:
    :param origin:
    :param destination:
    :param batch_size:
    :param strategy:
    :param output:
    :param keys:
    :param waypoints:
    :return:
    """
    if waypoints is None:
        waypoints = []
    if keys is None and register.keys:
        keys = [register.keys_balance.next]
    elif isinstance(keys, str):
        key = keys
    
    urls = []
    paths = [origin] + waypoints + [destination]
    if not waypoints:
        if isinstance(keys, list):
            key = random.choice(keys)
        urls.append(f"{host}?strategy={strategy}&origin={loc_to_str([origin])}&destination={loc_to_str([destination])}&output={output}&key={key}")
        return urls
    for idx in [(i, i + batch_size) for i in range(0, len(paths), batch_size)]:
        if isinstance(keys, list):
            key = random.choice(keys)
        tmp_points = paths[idx[0] - 1 if idx[0] > 1 else 0:idx[1]]
        if len(tmp_points) <= 2:
            urls.append(f"{host}?strategy={strategy}&origin={loc_to_str([tmp_points[0]])}&destination={loc_to_str([tmp_points[-1]])}&output={output}&key={key}")
        else:
            urls.append(f"{host}?strategy={strategy}&origin={loc_to_str([tmp_points[0]])}&destination={loc_to_str([tmp_points[-1]])}&waypoints={loc_to_str(tmp_points[1:-1])}&output={output}&key={key}")
    return urls


def request_navigating(url, idx, data_list):
    """
    通过导航url获取导航数据并进行结果设置
    :param url: 导航url
    :param idx: 结果集合索引
    :param data_list:
    :return:
    """
    try:
        data = register.session().get(url, timeout=2).json()
        if data['infocode'] == '10000':
            data_list[idx] = data
        else:
            raise Exception(data['infocode'])
    except Exception as e:
        register.logger.warning(f"Autonavi Error:{e},url:{url},url_idx:{idx}")


async def async_request_navigating(urls: List[str], data_list, idx=None):
    async with aiohttp.ClientSession() as session:
        tasks = []
        if idx:
            task = asyncio.ensure_future(do_async_request_navigating(session, urls, idx, data_list))
            tasks.append(task)
        else:
            for idx, url in enumerate(urls):
                if data_list[idx] is None:
                    task = asyncio.ensure_future(do_async_request_navigating(session, urls, idx, data_list))
                    tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)


def exchange_key(amap_url):
    # 再尝试换一个key获取一下
    all_token = amap_url.split('&')
    key_idx = -1
    for i, token in enumerate(all_token):
        if token.startswith("key"):
            old_key = token.split('=')[-1]
            register.keys_balance.reduce_weight(old_key)
            register.logger.error(f"futures_navigating request failed,key:{old_key},maybe need degradation")
            key_idx = i
    if key_idx > 0:
        all_token[key_idx] = f"key={register.keys_balance.next}"
    return "&".join(all_token)


async def do_async_request_navigating(session: aiohttp.ClientSession, urls, idx, data_list):
    try:
        async with session.get(urls[idx], timeout=aiohttp.ClientTimeout(total=2)) as response:
            data = await response.json()
            if data['infocode'] == '10000':
                data_list[idx] = data
            else:
                register.logger.warning(f"Autonavi Exchange URL:url_idx:{idx},url:{urls[idx]}")
                # 再尝试换一个key获取一下
                urls[idx] = exchange_key(urls[idx])
                async with session.get(urls[idx], timeout=aiohttp.ClientTimeout(total=2)) as re_resp:
                    new_data = await re_resp.json()
                    if new_data['infocode'] == '10000':
                        data_list[idx] = new_data
                    else:
                        urls[idx] = exchange_key(urls[idx])
                        
                        register.logger.warning(f"Autonavi Exchange URL But failed:url_idx:{idx},url:{urls[idx]}")
                        raise KeyError(data['infocode'] + new_data['infocode'])
    except Exception as e:
        register.logger.warning(f"Autonavi Error:{traceback.format_exc()},url_idx:{idx},url:{urls[idx]}")


def default_data_with_navigating_url(url, idx, data_list):
    points = []
    end_point = None
    for token in url.split('&'):
        if token.startswith("origin"):
            points.append(token.split('=')[-1])
        elif token.startswith("destination"):
            end_point = token.split('=')[-1]
        elif token.startswith("waypoints"):
            points.extend(token.split('=')[-1].split(';'))
    points.append(end_point)
    data_list[idx] = AMapDefaultResult(points=points).__dict__
    return data_list[idx]


def futures_navigating(urls: list, amap: bool = True) -> dict:
    """
    异步 基于 drive url list 通过请求高德接口 获得 路径规划结果
    :param urls:
    :param amap: 开关
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
    # 线程池
    # for idx in range(len(urls)):
    #     all_tasks.append(event_loop.run_in_executor(register.pool, request_navigating, urls[idx], idx, data_collections))
    # event_loop.run_until_complete(asyncio.wait(all_tasks))
    
    # 异步io
    if amap:
        event_loop.run_until_complete(async_request_navigating(urls, data_collections))
    # 获取结果,只获取 ['route']['paths'][0] ,也即只获取第一种策略的数据
    for idx in range(len(urls)):
        # 如果新url请求失败
        if not data_collections[idx]:
            if amap:
                register.logger.error(f"futures_navigating request failed,new url:{urls[idx]},url_idx:{idx}")
            data_collections[idx] = default_data_with_navigating_url(urls[idx], idx, data_collections)
        api_data_result = data_collections[idx]
        
        if not pack_data_result:
            pack_data_result = api_data_result
            pack_data_result['route']['paths'] = [pack_data_result['route']['paths'][0]]
        else:
            pack_data_result['route']['destination'] = api_data_result['route']['destination']
            
            pack_data_result['route']['taxi_cost'] = str(
                float(pack_data_result['route']['taxi_cost']) + float(api_data_result['route']['taxi_cost']))
            
            pack_data_result['route']['paths'][0]['distance'] = str(
                float(pack_data_result['route']['paths'][0]['distance']) + float(api_data_result['route']['paths'][0]['distance']))
            
            pack_data_result['route']['paths'][0]['duration'] = str(
                float(pack_data_result['route']['paths'][0]['duration']) + float(api_data_result['route']['paths'][0]['duration']))
            
            pack_data_result['route']['paths'][0]['tolls'] = str(
                float(pack_data_result['route']['paths'][0]['tolls']) + float(api_data_result['route']['paths'][0]['tolls']))
            
            pack_data_result['route']['paths'][0]['toll_distance'] = str(
                float(pack_data_result['route']['paths'][0]['toll_distance']) + float(
                    api_data_result['route']['paths'][0]['toll_distance']))
            
            pack_data_result['route']['paths'][0]['steps'].extend(api_data_result['route']['paths'][0]['steps'])
    
    return pack_data_result


def futures_driving(origin: list, destination: list, waypoints: list = None, strategy=5, output="json", key: str = None,
                    host: str = "https://restapi.amap.com/v3/direction/driving", batch_size: int = 12, amap: bool = True) -> dict:
    """
    异步进行导航url的构建,以及请求
    :param origin: [float,float]
    :param destination: [float,float]
    :param waypoints :[[float,float],[float,float],[float,float]]
    :param strategy: int 1-10
    :param output: str "json"
    :param key: str amap_web_api_key  "6828ea8c1670e149413299d8216c13ee"
    :param host: str host_name "https://restapi.amap.com/v3/direction/driving"
    :param batch_size: 每个url的batch
    :return:
    """
    if waypoints is None:
        waypoints = []
    if key is None and register.keys:
        key = register.keys_balance.next
    urls = navigating_url(host=host, origin=origin, destination=destination,
                          batch_size=batch_size,
                          strategy=strategy, waypoints=waypoints, output=output, keys=key)
    return futures_navigating(urls=urls, amap=amap)


def driving_batch(origin: list, destination: list, waypoints: list = None, check_points: tuple = ("到达途经地", "到达目的地"),
                  road_status_calculate: tuple = (0.5, ("畅通", "未知")), autonavi_config: dict = None):
    """
    批量异步的进行路径规划,并返回路径规划的结果
    :param origin:起始点 \n
    :param destination:终点 \n
    :param waypoints:途经点 \n
    :param check_points:检查点列表 tuple(检查点标识) \n
    :param road_status_calculate:路况 tuple(畅通路段系数,tuple(畅通路段标识))  计算公式:+(road_status_calculate[0])*road_distance if road_statu in road_status_calculate[1] else -(1-road_status_calculate[0])*road_distance \n
    :param autonavi_config: autonavi_config字典
        {
             strategy: int 1-10 \n
             output: str "json" \n
             key: str amap_web_api_key  "6828ea8c1670e149413299d8216c13ee" \n
             host: str host_name "https://restapi.amap.com/v3/direction/driving"
        }
    :return:[{'origin':[float,float],'destination':[float,float],'strategy':str,'total_duration':int,'total_distance':int,'assistant_action':int,'tmcs':float,'step':[{'distance':int,'duration':int,'polyline':str('float,float;float,float'}]}]
    """
    if waypoints is None:
        waypoints = []
    if autonavi_config is None:
        autonavi_config = {}
    data = futures_driving(origin=origin, destination=destination, waypoints=waypoints, **autonavi_config)
    if data['status'] != '1':
        return None
    route = data['route']
    origin_loc = format_loc(route['origin'])
    destination_loc = format_loc(route['destination'])
    route_path = route['paths'][0]
    waypoints_planning = {
        "origin": origin_loc,
        "destination": destination_loc,
        "strategy": route_path['strategy'],
        "total_duration": float(route_path['duration']),
        "total_distance": float(route_path['distance']),
        "steps": []
    }
    check_point = 1  # 检查点初始值
    total_waypoints = [origin] + waypoints + [destination]
    waypoints_step = list(zip(total_waypoints, total_waypoints[1:]))
    for idx, step in enumerate(route_path['steps']):
        road_status = sum([road_status_calculate[0] * float(tmc['distance'])
                           if tmc['status'] in road_status_calculate[1]
                           else -(1 - road_status_calculate[0]) * float(tmc['distance']) for tmc in
                           step['tmcs']])
        cur_check_point = 1 if step['assistant_action'] in check_points else 0  # 当前检查点值
        # 计算是否需要add/append,公式: old_check_point * (old_check_point or cur_check_point) = old_check_point
        if check_point * (check_point or cur_check_point) == 0:
            tmp_tmcs = waypoints_planning['steps'][-1]
            tmp_tmcs['polyline'] += ";" + step['polyline']
            tmp_tmcs['tmc'] += road_status
            tmp_tmcs['distance'] += float(step['distance'])
            tmp_tmcs['duration'] += float(step['duration'])
        else:
            step_tmcs = {
                "distance": float(step['distance']),
                "duration": float(step['duration']),
                "polyline": step['polyline'],
                "tmc": road_status,
                "origin": waypoints_step[len(waypoints_planning['steps'])][0],
                "destination": waypoints_step[len(waypoints_planning['steps'])][1],
            }
            waypoints_planning['steps'].append(step_tmcs)
            # print(waypoints_step[len(waypoints_planning['steps']) - 1][0], "=>", waypoints_step[len(waypoints_planning['steps']) - 1][1], step['polyline'], )
        
        check_point = cur_check_point
    
    return waypoints_planning
