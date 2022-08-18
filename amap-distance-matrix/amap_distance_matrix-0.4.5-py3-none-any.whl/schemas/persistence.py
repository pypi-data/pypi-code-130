# -*- coding: utf-8 -*- 
# Time: 2022-03-03 18:58
# Copyright (c) 2022
# author: Euraxluo

from typing import *
from pydantic import PrivateAttr, validator
from sqlalchemy import Column, String, Float, TIMESTAMP, text
from sqlalchemy.dialects.mysql import LONGTEXT
from .sqlalchemy_pydantic_orm import ORMBaseSchema
from amap_distance_matrix.services.register import register
import json


class EdgeORM(register.orm_base):
    """
    orm base model
    """
    __tablename__ = "distance_matrix_edge"
    __table_args__ = {"schema": "distance_matrix"}
    # id = Column(Integer, autoincrement=True)  # 如果id可以不为主键的话,则可以去掉 start 和 end 的index,可以现在mysql 需要 id primary_key ,才能,自动为其自己增加
    start = Column(String(16), nullable=False, primary_key=True)
    end = Column(String(16), nullable=False, primary_key=True)
    w_m_t = Column(String(8), nullable=False, primary_key=True)
    t = Column(String(2), nullable=False, index=True)
    origin = Column(String(32), nullable=False)  # List[float] 应该序列化为字符串
    destination = Column(String(32), nullable=False)  # List[float] 应该序列化为字符串
    distance = Column(Float)
    duration = Column(Float)
    polyline = Column(LONGTEXT)
    created_at = Column(TIMESTAMP, default=text('CURRENT_TIMESTAMP'))
    update_at = Column(TIMESTAMP, onupdate=text('CURRENT_TIMESTAMP'))


class EdgeDatabaseBase(ORMBaseSchema):
    """
    ORMBaseSchema Base schemas
    """
    start: str
    end: str
    w_m_t: str
    t: str
    origin: str
    destination: str
    distance: float
    duration: float
    polyline: str
    _orm_model = PrivateAttr(EdgeORM)


class EdgeGet(EdgeDatabaseBase):
    origin: List[float]
    destination: List[float]

    @validator('origin', 'destination', pre=True)
    def operator_origin_destination(cls, v, values, **kwargs):
        if isinstance(v, str):
            v = json.loads(v)
        return v


class EdgeUpsert(EdgeDatabaseBase):
    """
    CREATE/UPDATE model
    """
    t: Optional[str]  # is None,values are set for each check

    @validator('w_m_t', pre=True, always=True)
    def operator_w_m_t(cls, v, values, **kwargs):
        if len(v) == 5:
            values['t'] = v[-2:]
        return v

    @validator('t', always=True)
    def operator_t(cls, v, values, **kwargs):
        if 't' in values:
            v = values['t']
        return v or values.get('t', None)

    @validator('origin', 'destination', pre=True)
    def operator_origin_destination(cls, v, values, **kwargs):
        if isinstance(v, list):
            v = [round(v[0], 6), round(v[1], 6)]
            v = str(v)
        return v
