from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from .. import models
from .. import schemas


def createLogs(db: Session, logs: List[schemas.TaskLog]):
    response = []
    for log in logs:
        now = datetime.now()
        db_log = models.TaskLog(**log.dict(exclude_unset=True), datetime=now)
        db.add(db_log)
        db.commit()
        response.append({**log.dict(exclude_unset=True), "datetime": now})
    return response


def getLogs(db: Session, limit: int, offset: int, id: str):
    if id:
        return db.query(models.TaskLog).filter(models.TaskLog.id == id).offset(offset).limit(limit).all()
    return db.query(models.TaskLog).offset(offset).limit(limit).all()
