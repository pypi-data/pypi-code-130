from typing import List, Union
from fastapi import status
from sqlalchemy.orm import Session, Query
from .. import models
from .. import schemas


############
### c2db ###
############
def createC2db(db: Session, datas: List[schemas.C2db]):
    response = []
    for data in datas:
        if not db.query(models.C2db).filter(models.C2db.ID == data.ID).first():
            db_ribbon = models.C2db(**data.dict(exclude_unset=True))
            db.add(db_ribbon)
            response.append(
                {"status": "创建成功", "id": data.ID, "formula": data.Formula, "code": status.HTTP_201_CREATED})
        else:
            response.append(
                {"status": "记录已存在，请勿重复创建", "id": data.ID, "formula": data.Formula,
                 "code": status.HTTP_202_ACCEPTED})
    db.commit()
    return response


def getC2dbById(db: Session, id_: str):
    return db.query(models.C2db).filter(models.C2db.ID == id_).first()


def queryC2db(db: Session,
              id: Union[str, None] = None,
              skip: int = 0,
              limit: int = 100,
              min_band_gap: Union[float, None] = None,
              max_band_gap: Union[float, None] = None):
    db_query: Union[Query, None] = db.query(models.C2db)
    if id:
        db_query = db_query.filter(models.C2db.ID == id)
    if min_band_gap:
        db_query = db_query.filter(models.C2db.Band_gap > min_band_gap)
    if max_band_gap:
        db_query = db_query.filter(models.C2db.Band_gap <= max_band_gap)
    return db_query.offset(skip).limit(limit).all()