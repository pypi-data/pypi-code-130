# -*- coding: utf-8 -*- 
# Time: 2022-03-04 16:31
# Copyright (c) 2022
# author: Euraxluo


from functools import partial, lru_cache
from amap_distance_matrix.services.dishashing import *
from amap_distance_matrix.services.navigation import *
from amap_distance_matrix.helper import *


def distance_matrix(*points: List[float],
                    time_slot: str = None,
                    autonavi_config: Dict = None,
                    edge_key: str = "",
                    geo_key: str = "",
                    expire: int = 1209600,
                    geo_wide: int = 200,
                    strictly_constrained: bool = False) -> Tuple[Dict[int, dict], Dict[int, dict], Dict[int, Dict]]:
    """
    根据点,获取其距离矩阵,
    :param strictly_constrained: 是否强约束,如果强约束,
    :param geo_wide:
    :param time_slot:
    :param edge_key:
    :param geo_key:
    :param expire:
    :param points:
    :param autonavi_config: autonavi_config字典
    {
         strategy: int 1-10 \n
         output: str "json" \n
         key: str amap_web_api_key  "6828ea8c1670e149413299d8216c13ee" \n
         host: str host_name "https://restapi.amap.com/v3/direction/driving"
    }
    :return 返回 距离矩阵,时间矩阵,边矩阵
    """
    if not edge_key:
        edge_key = register.edge_key
    if not geo_key:
        geo_key = register.geo_key
    # 1.生成点对并排序
    edge_sorted = point_pairing_sorted(*points)
    if time_slot is None:
        time_slot = time_slot_wmh()[-2:]

    waypoints = []
    for i, edge_points in enumerate(edge_sorted):
        waypoints.append(edge_points[0])
        if i == len(edge_sorted) - 1:
            waypoints.append(edge_points[1])
    route_edges = waypoints_route(*waypoints, time_slot=time_slot, autonavi_config=json.dumps(autonavi_config), edge_key=edge_key, geo_key=geo_key, expire=expire, geo_wide=geo_wide, strictly_constrained=strictly_constrained)
    distances = {}
    durations = {}
    edges = {}
    calculate_cache = {}
    for o_id, i in enumerate(points):
        i = tuple(i)
        distances[o_id] = {}
        durations[o_id] = {}
        edges[o_id] = {}
        for d_id, j in enumerate(points):
            j = tuple(j)
            if i == j:
                distances[o_id][d_id] = 0
                durations[o_id][d_id] = 0
                edges[o_id][d_id] = Edge(w_m_t=time_slot_wmh(), origin=i, destination=j).dict()
                continue
            elif (i, j) in edge_sorted:
                index = edge_sorted.index((i, j))
            elif (j, i) in edge_sorted:
                index = edge_sorted.index((j, i))
            else:
                if (i, j) in calculate_cache:
                    co_id, cd_id = calculate_cache[(i, j)]
                    distance_tmp = distances[co_id][cd_id]
                    duration_tmp = durations[co_id][cd_id]
                    edge_tmp = edges[co_id][cd_id]
                elif (j, i) in calculate_cache:
                    co_id, cd_id = calculate_cache[(j, i)]
                    distance_tmp = distances[co_id][cd_id]
                    duration_tmp = durations[co_id][cd_id]
                    edge_tmp = edges[co_id][cd_id]
                else:
                    i_j_route = waypoints_route(i, j, time_slot=time_slot, autonavi_config=json.dumps(autonavi_config), edge_key=edge_key, geo_key=geo_key, expire=expire, geo_wide=geo_wide, strictly_constrained=strictly_constrained)
                    distance_tmp = int(i_j_route[0]['distance'])
                    duration_tmp = int(i_j_route[0]['duration'])
                    edge_tmp = i_j_route[0]

                distances[o_id][d_id] = distance_tmp
                durations[o_id][d_id] = duration_tmp
                edges[o_id][d_id] = edge_tmp
                calculate_cache[(i, j)] = (o_id, d_id)
                continue
            distances[o_id][d_id] = int(route_edges[index]['distance'])
            durations[o_id][d_id] = int(route_edges[index]['duration'])
            edges[o_id][d_id] = route_edges[index]
    return distances, durations, edges


def driving_route(waypoints: List[List[float]],
                  autonavi_config: Dict = None,
                  edge_key: str = "",
                  geo_key: str = "",
                  expire: int = 1209600):
    """
    通过获取高德Webapi得到导航结果,并且进行缓存
    :param edge_key:
    :param geo_key:
    :param expire:
    :param waypoints:
    :param autonavi_config: autonavi_config字典
    {
         strategy: int 1-10 \n
         output: str "json" \n
         key: str amap_web_api_key  "6828ea8c1670e149413299d8216c13ee" \n
         host: str host_name "https://restapi.amap.com/v3/direction/driving"
    }
    :return:
    """
    if not edge_key:
        edge_key = register.edge_key
    if not geo_key:
        geo_key = register.geo_key
    if len(waypoints) < 2:
        raise ValueError("waypoints length must greater than 2")
    driving_batch_result = driving_batch(origin=waypoints[0], waypoints=waypoints[1:-1], destination=waypoints[-1], autonavi_config=autonavi_config)

    all_edge = []
    for i, _ in enumerate(zip(waypoints, waypoints[1:])):
        step = driving_batch_result['steps'][i]
        all_edge.append(Edge(**step))

    func = partial(edge_hash, edge_key=edge_key, geo_key=geo_key, expire=expire)
    register.pool.submit(func, *[Edge(**i) for i in driving_batch_result['steps']])
    return driving_batch_result


# @ignore_unhashable
# @lru_cache()
def waypoints_route(*waypoints: Union[List[float], Tuple[float]],
                    time_slot: str = None,
                    autonavi_config: Union[Dict, str] = None,
                    edge_key: str = "",
                    geo_key: str = "",
                    expire: int = 1209600,
                    geo_wide: int = 200,
                    strictly_constrained: bool = False) -> Union[list, List[None]]:
    """
    线路的途径数据,没有缓存的将会获取高德导航结果,并且进行缓存后返回
    :param strictly_constrained: 是否强约束,如果强约束,
    :param geo_wide:
    :param time_slot:
    :param edge_key:
    :param geo_key:
    :param expire:
    :param waypoints:
    :param autonavi_config: autonavi_config字典
    {
         strategy: int 1-10 \n
         output: str "json" \n
         key: str amap_web_api_key  "6828ea8c1670e149413299d8216c13ee" \n
         host: str host_name "https://restapi.amap.com/v3/direction/driving"
    }
    """
    if not edge_key:
        edge_key = register.edge_key
    if not geo_key:
        geo_key = register.geo_key
    # 1. 先获取geohash
    if isinstance(autonavi_config, str):
        autonavi_config = json.loads(autonavi_config)

    if len(waypoints) < 2:
        return []
    edges = []
    for b, e in zip(waypoints, waypoints[1:]):
        edges.append([b, e])

    if time_slot is None:
        time_slot = time_slot_wmh()[-2:]
    get_edges = edge_get(*edges, dist=int(geo_wide / 2), time_slot=time_slot, edge_key=edge_key, geo_key=geo_key, geo_wide=geo_wide, strictly_constrained=strictly_constrained)
    result = [None] * len(get_edges)
    need_calculate_waypoints = []
    need_calculate_waypoints_result_idx: List[int] = []
    for i, ((start, end), (start_geohash, end_geohash, edge)) in enumerate(zip(edges, get_edges)):
        if start_geohash != end_geohash and edge['distance'] == 0:
            if need_calculate_waypoints and need_calculate_waypoints[-1] != start:
                need_calculate_waypoints.append(end)
                need_calculate_waypoints_result_idx.append(i)
            else:
                if need_calculate_waypoints:
                    need_calculate_waypoints_result_idx.append(None)
                need_calculate_waypoints_result_idx.append(i)
                need_calculate_waypoints.append(start)
                need_calculate_waypoints.append(end)
        else:
            result[i] = edge
    if not need_calculate_waypoints:
        return result
    driving_result = driving_route(need_calculate_waypoints, autonavi_config=autonavi_config, edge_key=edge_key, geo_key=geo_key, expire=expire)
    register.logger.info(f"route_waypoints get driving and cache {len(driving_result['steps'])}")
    for i, edge in enumerate(driving_result['steps']):
        if need_calculate_waypoints_result_idx[i] is not None:
            result[need_calculate_waypoints_result_idx[i]] = Edge(**edge).dict()
    return result
