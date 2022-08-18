# -*- coding: utf-8 -*- 
# Time: 2022-03-01 15:43
# Copyright (c) 2022
# author: Euraxluo

from typing import *
from amap_distance_matrix.helper import haversine,format_loc

class AMapDefaultResultRouteStep(object):
    def __init__(self, start: str, end: str):
        self.polyline: str
        self.instruction = "到达途经地"
        self.orientation = "北"
        self.road = "road"
        self.distance = haversine(format_loc(start),format_loc(end))*1.5
        self.tolls = "0"
        self.toll_distance = "0"
        self.toll_road = []
        self.duration = self.distance/(25000/60/60)
        self.action = []
        self.assistant_action = "到达途经地"
        self.tmcs: List
        self.polyline = start + ";" + end
        self.tmcs = [
            {
                "lcode": [],
                "distance": "0",
                "status": "畅通",
                "polyline": self.polyline
            }
        ]


class AMapDefaultResultPath(object):
    def __init__(self, steps: List[AMapDefaultResultRouteStep]):
        self.distance = "0"
        self.duration = "0"
        self.strategy = "速度最快"
        self.tolls = "0"
        self.toll_distance = "0"
        self.steps = [i.__dict__ for i in steps]
        self.restriction = "0"
        self.traffic_lights = "0"


class AMapDefaultResultRoute(object):
    def __init__(self, paths: AMapDefaultResultPath):
        self.origin = "0"
        self.destination = "0"
        self.taxi_cost = "0"
        self.paths = [paths.__dict__]


class AMapDefaultResult(object):
    def __init__(self, points: List[str]):
        self.status = "1"
        self.info = "OK"
        self.infocode = "10000"
        self.count = "1"
        self.route: AMapDefaultResultRoute
        steps = []
        for i, point in enumerate(points):
            if i == 0:
                continue
            steps.append(AMapDefaultResultRouteStep(start=points[i - 1], end=point))

        self.route = AMapDefaultResultRoute(paths=AMapDefaultResultPath(steps=steps)).__dict__
