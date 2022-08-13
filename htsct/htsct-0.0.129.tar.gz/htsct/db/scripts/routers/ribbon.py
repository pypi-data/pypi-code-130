from typing import List
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from .. import crud, schemas
from .. import depends
from ..database import get_db

router = APIRouter(
    tags=["ribbon"],
)


@router.put("/updateRibbon", response_model=List[schemas.RibbonResponseModel])
def updateRibbon(ribbons: List[schemas.Ribbon], db: Session = Depends(get_db)):
    return crud.updateRibbon(db=db, ribbons=ribbons)


@router.post("/createRibbon", response_model=List[schemas.RibbonResponseModel])
def createRibbon(ribbons: List[schemas.Ribbon], db: Session = Depends(get_db)):
    return crud.createRibbon(db, ribbons=ribbons)


@router.get("/ribbons", response_model=List[schemas.Ribbon])
def queryRibbons(query=Depends(depends.queryRibbons)):
    return query


@router.delete("/delRibbon", response_model=schemas.RibbonResponseModel)
def delRibbon(id: str, db: Session = Depends(get_db)):
    return crud.delRibbon(db, id)


@router.get("/getRibbonRunningStatus", response_model=schemas.RibbonRunStatusResponse)
def getRibbonRunningStatus(id: str, db: Session = Depends(get_db)):
    return crud.getRunningStatus(db, id)


@router.put("/updateRibbonRunningStatus", response_model=schemas.RibbonRunStatusResponse,
            description="更新Ribbon的计算状态")
def updateRunningStatus(id: str, isRunning: bool, db: Session = Depends(get_db)):
    return crud.updateRunningStatus(db, id, isRunning)


@router.put("/updateAllInfo", response_model=List[schemas.RibbonInfoUpdateResponse])
def updateAllInfo(infos: List[schemas.RibbonInfos], db: Session = Depends(get_db)):
    return crud.updateAllInfo(db, infos)


@router.get("/getAllInfo", response_model=List[schemas.RibbonInfoResponse])
def getAllInfo(limit: int = 10, skip: int = 0, db: Session = Depends(get_db)):
    return crud.getAllInfo(db, limit, skip)
