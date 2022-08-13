from typing import List, Union
import json
from fastapi import status
from sqlalchemy.orm import Session, Query
from .. import models
from .. import schemas


##############
### ribbon ###
##############
def getRibbonById(db: Session, id_: str):
    return db.query(models.Ribbon).filter(models.Ribbon.id == id_).first()


def updateRibbon(db: Session, ribbons: List[schemas.Ribbon]):
    response = []
    for ribbon in ribbons:
        if not getRibbonById(db, ribbon.id):
            response.append(
                {"status": "记录不存在，请新建", "id": ribbon.id, "formula": ribbon.formula, "code": status.HTTP_404_NOT_FOUND})
            continue
        db.query(models.Ribbon).filter(models.Ribbon.id == ribbon.id).update(ribbon.dict(exclude_unset=True))
        response.append(
            {"status": "update succeed", "id": ribbon.id, "formula": ribbon.formula, "code": status.HTTP_200_OK})
    db.commit()
    return response


def createRibbon(db: Session, ribbons: List[schemas.Ribbon]):
    response = []
    for ribbon in ribbons:
        if getRibbonById(db, ribbon.id):
            response.append(
                {"status": "记录已存在，请勿重复创建", "id": ribbon.id, "formula": ribbon.formula,
                 "code": status.HTTP_202_ACCEPTED})
            continue
        db_ribbon = models.Ribbon(**ribbon.dict(exclude_unset=True))
        db.add(db_ribbon)
        response.append(
            {"status": "创建成功", "id": ribbon.id, "formula": ribbon.formula, "code": status.HTTP_201_CREATED})
    db.commit()
    return response


def queryRibbon(db: Session, *, id, c2db_ID, skip, limit, work_path, description, **params):
    db_query: Union[Query, None] = db.query(models.Ribbon)
    #
    if id:
        db_query = db_query.filter(models.Ribbon.id == id)
    if c2db_ID:
        db_query = db_query.filter(models.Ribbon.c2db_ID == c2db_ID)
    if work_path:
        db_query = db_query.filter(models.Ribbon.work_path.like(f"%{work_path}%"))
    if description:
        db_query = db_query.filter(models.Ribbon.description == description)
    for k, v in params.items():
        if k.startswith("min_") and v is not None:
            k = k.lstrip("min_")
            db_query = db_query.filter(getattr(models.Ribbon, k) > v)
        if k.startswith("max_") and v is not None:
            k = k.lstrip("max_")
            db_query = db_query.filter(getattr(models.Ribbon, k) <= v)
    return db_query.offset(skip).limit(limit).all()


def delRibbon(db: Session, id_: str):
    ribbon = getRibbonById(db, id_)
    if ribbon:
        db.query(models.Ribbon).filter(models.Ribbon.id == id_).delete()
        db.commit()
        return {"status": "删除成功", "id": ribbon.id, "formula": ribbon.formula, "code": status.HTTP_200_OK}
    return {"status": "记录不存在", "id": None, "formula": None, "code": status.HTTP_200_OK}


def getRunningStatus(db: Session, id: str):
    ribbon = db.query(models.Ribbon).filter(models.Ribbon.id == id).first()
    info = json.loads(ribbon.info)
    return {"isRunning": info["isRunning"], "code": 200, "status": "查询成功"}


def getAllInfo(db: Session, limit, skip):
    ribbons = db.query(models.Ribbon).all()
    return [{"id": ribbon.id, "info": json.loads(ribbon.info)} for ribbon in ribbons][skip:limit]


def updateAllInfo(db: Session, infos: List[schemas.RibbonInfos]):
    response = []
    for info in infos:
        data = {"info": json.dumps(info.info.dict(exclude_unset=True))}
        db.query(models.Ribbon).filter(models.Ribbon.id == info.id).update(data)
        db.commit()
        response.append({"status": "update succeed", "id": info.id, "code": status.HTTP_200_OK})
    return response


def updateRunningStatus(db: Session, id: str, isRunning: bool):
    ribbon = db.query(models.Ribbon).filter(models.Ribbon.id == id).first()
    info = json.loads(ribbon.info)
    info.update({"isRunning": isRunning})
    info = json.dumps(info)
    db.query(models.Ribbon).filter(models.Ribbon.id == id).update({"id": id, "info": info})
    db.commit()
    return {"isRunning": isRunning, "code": 200, "status": "修改成功"}
