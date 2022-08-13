from typing import List, Union

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    tags=["config"],
)


@router.post("/config", response_model=List[schemas.Config])
def createConfig(configs: List[schemas.Config], db: Session = Depends(get_db)):
    return crud.createConfig(db, configs)


@router.get("/config", response_model=List[schemas.FullConfig])
def getConfig(limit: int = 100, offset: int = 0, id: Union[str, None] = None, db: Session = Depends(get_db)):
    return crud.getConfig(db, id, limit, offset)


@router.delete("/config", response_model=schemas.Config)
def deleteConfig(id: str, db: Session = Depends(get_db)):
    return crud.deleteConfig(db, id)


@router.put("/config", response_model=List[schemas.Config])
def updateConfig(configs: List[schemas.Config], db: Session = Depends(get_db)):
    return crud.updateConfig(db, configs)


@router.put("/activeConfig", response_model=schemas.Config)
def setActive(id: str, db: Session = Depends(get_db)):
    return crud.setActive(db, id)


@router.get("/activeconfig", response_model=schemas.Config)
def getActive(db: Session = Depends(get_db)):
    return crud.getActive(db)
