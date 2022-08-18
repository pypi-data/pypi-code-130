# -*- coding: utf-8 -*- 
# Time: 2022-03-02 17:18
# Copyright (c) 2022
# author: Euraxluo

import redis
import json
import time
import copy
import threading
from amap_distance_matrix.services.register import register
from amap_distance_matrix.schemas.dishashing import *
from amap_distance_matrix.helper import *

script_lock = threading.Lock()


def edge_hash(*edges: Edge, edge_key: str = "", geo_key: str = "", expire: int = 1209600):
    """
    针对边的详细信息进行存储
    :param expire: 边缓存过期时间,默认两周
    :param edge_key:边的key,主要用于分区
    :param geo_key:点的key,主要用于分区
    :param edges:
    :return:
    """
    if not edge_key:
        edge_key = register.edge_key
    if not geo_key:
        geo_key = register.geo_key

    with register.redis.pipeline(transaction=False) as pip:
        for edge in edges:
            b_geohash = geo_encode(*edge.origin)
            e_geohash = geo_encode(*edge.destination)
            pip.execute_command('GEOADD', geo_key,
                                *[edge.origin[0], edge.origin[1], b_geohash, edge.destination[0], edge.destination[1],
                                  e_geohash])
            pip.hset(name=edge_key + ':' + b_geohash + ':' + e_geohash, key=edge.w_m_t, value=edge.json())
            pip.expire(edge_key + ':' + b_geohash + ':' + e_geohash, expire)  # 两周的过期时间

            # 更新key列表
            pip.zremrangebyscore(register.geohashing_keys, 0, time.time() - expire)
            add_item = {edge_key + ':' + b_geohash + ':' + e_geohash: time.time()}
            pieces = []
            for pair in add_item.items():
                pieces.append(pair[1])
                pieces.append(pair[0])
            pip.execute_command('ZADD', register.geohashing_keys, *pieces)
        res = pip.execute()
        log_result = [res[i:i + 5] for i in range(0, len(res), 5)]
        log_result = [sum([i[idx] for i in log_result]) for idx in range(5)]

        register.logger.info(
            f"edge_hash: hashing_edges:{len(edges)},geo_add:{log_result[0]},edge_hash:{log_result[1]},zset_remove:{log_result[3]},zset_add:{log_result[4]}")


def edge_list() -> Generator:
    """
    获取 redis 中存储的所有edge
    :return: yield hashkey,filedname,value
    """
    # 1.获取到所有可以进行存储的key
    result = register.redis.zrangebyscore(register.geohashing_keys, min=0, max=time.time())
    # 2.挨个扫描这些key的field,并返回
    geohashing_keys = []
    for hkey in result:
        if isinstance(hkey, bytes):
            hkey = str(hkey, encoding='utf8')
        geohashing_keys.append(hkey)
        res = hashset_scan(hkey)
        for k, v in res.items():
            yield hkey, k, v


def hashset_scan(hkey: str, page_size: int = None):
    with register.redis.pipeline(transaction=False) as pipe:
        page_number = -1
        scans = {}
        while page_number != 0:
            if page_number == -1:
                page_number = 0
            pipe.hscan(hkey, page_number, '*', page_size)
            page_number, data = pipe.execute()[0]
            for k, v in data.items():
                if isinstance(k, bytes):
                    k = str(k, encoding='utf8')
                if isinstance(v, bytes):
                    v = str(v, encoding='utf8')
                scans[k] = v
        return scans


def edge_keys(edge_endpoints: List[List[str]] = None) -> Tuple[Set, Set, List]:
    """
    可以快速检查redis是否缓存
    :param edge_endpoints: 在迭代时进行check,判断redis 是否缓存
    :return: Tuple[Set,Set,List],(Set:edge_endpoints 中存在缓存的数据的索引,Set:edge_endpoints 中 不存在缓存的数据的索引,List:Redis中缓存的边的key)
    :return: Tuple[Set,Set,List],(Set:edge_endpoints 中存在缓存的数据的索引,Set:edge_endpoints 中 不存在缓存的数据的索引,List:Redis中缓存的边的key)
    """
    if edge_endpoints is None:
        edge_endpoints = []
    result = register.redis.zrangebyscore(register.geohashing_keys, min=0, max=time.time())
    geohashing_keys = []
    contain = set()
    for i in result:
        if isinstance(i, bytes):
            i = str(i, encoding='utf8')
        k = i.split(':')
        geohashing_keys.append(i)
        edge_endpoint_list = [k[1], k[2]]
        if edge_endpoint_list in edge_endpoints:
            contain.add(edge_endpoints.index(edge_endpoint_list))
    return contain, set(range(len(edge_endpoints))) - contain, geohashing_keys


def _script_load(script):
    sha = [None]

    def call(conn, keys=None, args=None, force_eval=False):
        if args is None:
            args = []
        if keys is None:
            keys = []
        if not force_eval:
            # 加载并缓存校验和
            if not sha[0]:
                script_lock.acquire()
                if isinstance(conn, redis.client.Pipeline):
                    conn.execute_command("SCRIPT", "LOAD", script, parse="LOAD")
                    sha[0] = conn.execute()[-1]
                else:
                    sha[0] = conn.execute_command("SCRIPT", "LOAD", script, parse="LOAD")
                script_lock.release()
            try:
                return conn.execute_command("EVALSHA", sha[0], len(keys), *(keys + args))
            except redis.exceptions.ResponseError as msg:
                if not msg.args[0].startswith("NOSCRIPT"):
                    raise
        # 如果需要强制执行或者脚本接收到错误时，会使用eval执行脚本，eval执行完脚本后，会把脚本的sha1值缓存下来
        return conn.execute_command("EVAL", script, len(keys), *(keys + args))

    return call


_acquire_edge = _script_load(
    # 1. 不存在,返回nil
    # 2. 扫描
    # 3. 扩大范围扫描
    """
    local radius_keys = {}
    local radius_keys_dist = {}
    local near_endpoint = {}
    local scans = nil
    local bs = redis.call('georadius',KEYS[2],ARGV[3],ARGV[4],ARGV[7],ARGV[8],'COUNT',3,'WITHDIST')
    local es =  redis.call('georadius',KEYS[2],ARGV[5],ARGV[6],ARGV[7],ARGV[8],'COUNT',3,'WITHDIST')

    for _,b in ipairs(bs) do
        for _,e in ipairs(es) do
            radius_keys[#radius_keys+1] = {b[1],e[1]}
            radius_keys_dist[#radius_keys_dist+1] = b[2]+e[2]
            near_endpoint[#near_endpoint+1] = {b[1],e[1],b[2]+e[2]}
        end
    end
    for _,e in ipairs(es) do
        for _,b in ipairs(bs) do
            radius_keys[#radius_keys+1] = {e[1],b[1]}
            radius_keys_dist[#radius_keys_dist+1] = e[2]+b[2]
            near_endpoint[#near_endpoint+1] = {e[1],b[1],e[2]+b[2]}
        end
    end
    for i,ks in ipairs(radius_keys) do
        local key = KEYS[1] .. ':' .. ks[1] .. ':' .. ks[2]
        if radius_keys_dist[i] < ARGV[9]+0 and ARGV[10] == '0' then
            scans = redis.call('hscan',key,0,'match','*','count',ARGV[2])
        else
            scans = redis.call('hscan',key,0,'match',ARGV[1],'count',ARGV[2])
        end
        local fields = scans[2]
        local ids = {}
        for k, v in ipairs(fields) do
            if k % 2 == 0 then
                ids[#ids + 1] = {ks[1],ks[2],v}
            end
        end
        if (#fields >0) then
            return ids
        end            
    end
    return near_endpoint
    """
)


def edge_get(*edges: Tuple[List[float]], dist: int = 200, unit: str = 'm', time_slot: str = None,
             edge_key: str = "", geo_key: str = "", geo_wide: int = 200,
             strictly_constrained: bool = False):
    """
    根据 起点和终点经纬度获取边信息
    :param strictly_constrained: 强约束,0/False为非强约束,1/True 为强约束
    :param geo_wide: 搜索范围约束,单位m,默认200m,即经纬度偏移之和200m
    :param time_slot: 时间段,如果为None,则设置为当前 time_slot
    :param edges: (([lon,lat],[lon,lat]),([lon,lat],[lon,lat]),...)
    :param dist:搜索时距离约束
    :param unit:搜索单位
    :param edge_key:edge点存储key,主要用于分区
    :param geo_key:geo点存储key,主要用于分区
    :return:
    """
    if not edge_key:
        edge_key = register.edge_key
    if not geo_key:
        geo_key = register.geo_key
    result = []
    if strictly_constrained:
        strictly_constrained = 1
    else:
        strictly_constrained = 0
    if time_slot is None:
        time_slot = time_slot_wmh()[-2:]
    with register.redis.pipeline(transaction=False) as pip:
        for edge in edges:
            b_geohash = geo_encode(*edge[0])
            e_geohash = geo_encode(*edge[1])
            _acquire_edge(pip, [edge_key, geo_key],
                          [f"???{time_slot}", 7, edge[0][0], edge[0][1], edge[1][0], edge[1][1], dist, unit, geo_wide,
                           strictly_constrained], force_eval=True)
            # _acquire_edge(pip, [edge_key, b_geohash, e_geohash, geo_key], [f"???{time_slot}", 7, edge[0][0], edge[0][1], edge[1][0], edge[1][1], dist, unit, geo_wide, strictly_constrained])
        edges_list = pip.execute()
        for el, edge in zip(edges_list, edges):
            b_geohash = geo_encode(*edge[0])
            e_geohash = geo_encode(*edge[1])
            if len(el) == 0:
                el.append([b_geohash, e_geohash, Edge(w_m_t=time_slot_wmh(), origin=edge[0], destination=edge[1]).dict()])
            elif len(el) >= 1 and isinstance(el[0][2], int):
                el.sort(key=lambda x: x[2])
                el[0][2] = Edge(w_m_t=time_slot_wmh(), origin=edge[0], destination=edge[1]).dict()
            elif isinstance(el[0][2], str):
                el.sort(key=lambda x: abs(int(json.loads(x[2])['w_m_t'][-2:]) - int(time_slot)) if time_slot.isdigit() else 0)
                el[0][2] = json.loads(el[0][2])
            elif isinstance(el[0][2], bytes):
                el.sort(key=lambda x: abs(int(json.loads(str(x[2], encoding='utf8'))['w_m_t'][-2:]) - int(
                    time_slot)) if time_slot.isdigit() else 0)
                el[0][2] = json.loads(str(el[0][2], encoding='utf8'))

            for idx, ei in enumerate(el[0]):
                if isinstance(ei, bytes):
                    el[0][idx] = str(ei, encoding='utf8')
            nearest = copy.deepcopy(el[0])
            result.append(nearest)
        del edges_list
        return result
