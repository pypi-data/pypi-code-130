from typing import List

from sqlalchemy.orm import Session

from .. import models
from .. import schemas


def createConfig(db: Session, configs: List[schemas.Config]):
    for config in configs:
        db_config = models.Config(**config.dict(exclude_unset=True), active=False if getActive(db) else True)
        db.add(db_config)
        db.commit()
    return configs


def getConfig(db: Session, id: str, limit: int, offset: int):
    if id:
        return db.query(models.Config).filter(models.Config.id == id).offset(offset).limit(limit).all()
    return db.query(models.Config).offset(offset).limit(limit).all()


def updateConfig(db: Session, configs: List[schemas.Config]):
    for config in configs:
        db.query(models.Config).filter(models.Config.id == config.id).update(config.dict(exclude_unset=True))
    db.commit()
    return [db.query(models.Config).filter(models.Config.id == config.id).first() for config in configs]


def deleteConfig(db: Session, id: str):
    response = db.query(models.Config).filter(models.Config.id == id).first()
    db.query(models.Config).filter(models.Config.id == id).delete()
    db.commit()
    return response if response else {"id": "-1"}


def setActive(db: Session, id: str):
    actives = db.query(models.Config).filter(models.Config.active == 1).all()
    for active in actives:
        db.query(models.Config).filter(models.Config.id == active.id).update({"active": False})
    db.query(models.Config).filter(models.Config.id == id).update({"active": True})
    db.commit()
    return db.query(models.Config).filter(models.Config.active == 1).first()


def getActive(db: Session):
    return db.query(models.Config).filter(models.Config.active == 1).first()
