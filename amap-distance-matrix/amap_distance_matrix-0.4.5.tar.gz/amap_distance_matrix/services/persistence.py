# -*- coding: utf-8 -*- 
# Time: 2022-03-03 18:49
# Copyright (c) 2022
# author: Euraxluo


from amap_distance_matrix.schemas.persistence import EdgeGet, EdgeORM, EdgeUpsert
from amap_distance_matrix.services.dishashing import *

from sqlalchemy.dialects.mysql import insert
from sqlalchemy import text

register.orm_base.metadata.create_all(bind=register.orm_engine, checkfirst=True)


def edge_persistence():
    """
    边数据同步,将redis的边数据,同步到MYSQL中
    :return:
    """
    with register.orm() as db:
        data = []
        for k, f, v in edge_list():
            item = k.split(':')
            _, start, end = item[0:-3], item[-2], item[-1]
            data_item = EdgeUpsert(start=start, end=end, **json.loads(v))
            if data_item.distance == 0:
                continue
            data.append(data_item.dict())
        try:
            upsert(db, EdgeORM, data)
        except Exception as e:
            register.logger.error(f"Edge Persistence Error:{e},data_len:{len(data)},data:{data[0]}")


def upsert(session, model: EdgeORM, rows: List[dict], batch_size: int = 200):
    table = model.__table__
    update_cols = [c.name for c in table.c
                   if c not in list(table.primary_key.columns)]

    for idx in [(i, i + batch_size) for i in range(0, len(rows), batch_size)]:
        tmp_rows = rows[idx[0]:idx[1]]
        insert_stmt = insert(table).values(tmp_rows)

        on_duplicate_stmt = insert_stmt.on_duplicate_key_update(
            **{k: getattr(insert_stmt.inserted, k) if k != "update_at" else text('CURRENT_TIMESTAMP') for k in update_cols},
        )
        session.execute(on_duplicate_stmt)
        session.commit()


def get_edge(start: List[float] = None, end: List[float] = None, w_m_t: str = None, t: str = None, skip: int = 0, limit: int = 100):
    """
    根据筛选字段获取mysql中存储的边数据
    :param start: 边起点
    :param end: 边终点
    :param w_m_t: 边的计算时间数据
    :param t: 边的计算时间段
    :param skip: 分页用
    :param limit: 分页用,page size
    :return:
    """
    origins = {
        EdgeORM.start: geo_encode(start[0], start[1]) if start else None,
        EdgeORM.end: geo_encode(end[0], end[1]) if end else None,
        EdgeORM.w_m_t: w_m_t if w_m_t else None,
        EdgeORM.t: t if t else None,
    }
    filters = {k == v for k, v in origins.items() if v is not None}
    result = []
    if not filters:
        return result

    with register.orm() as db:
        edges = db.query(EdgeORM).filter(*filters).offset(skip).limit(limit).all()
        for edge in edges:
            result.append(EdgeGet.from_orm(edge).dict())
    return result
