from typing import List, Union

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    tags=["taskLog"],
)


@router.post("/taskLog", response_model=List[schemas.TaskLogResponse])
def createTaskLog(logs: List[schemas.TaskLog], db: Session = Depends(get_db)):
    return crud.createLogs(db, logs)


@router.get("/taskLog", response_model=List[schemas.TaskLogResponse])
def getTaskLog(limit: int = 100, offset: int = 0, id: Union[str, None] = None, db: Session = Depends(get_db)):
    return crud.getLogs(db, limit, offset, id)
