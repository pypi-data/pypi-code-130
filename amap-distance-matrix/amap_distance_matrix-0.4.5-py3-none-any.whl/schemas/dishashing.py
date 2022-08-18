# -*- coding: utf-8 -*- 
# Time: 2022-03-02 17:58
# Copyright (c) 2022
# author: Euraxluo

from typing import *
from pydantic import BaseModel, validator
from amap_distance_matrix.helper import time_slot_wmh


class EdgeBase(BaseModel):
    w_m_t: Optional[str]  # w0d0t,default can be None,validator can auto set
    distance: float = 0
    duration: float = 0


class Edge(EdgeBase):
    polyline: str = ''
    origin: List[float]
    destination: List[float]

    @validator('w_m_t', always=True)
    def auto_set_wmt(cls, v, values, **kwargs):
        if not v:
            v = time_slot_wmh()
        return v
