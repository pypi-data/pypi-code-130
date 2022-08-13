from typing import List
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from .. import crud, schemas
from .. import depends
from ..database import get_db

router = APIRouter(
    tags=["c2db"],
)


@router.post("/createC2db", response_model=List[schemas.C2dbResponseModel])
def createC2db(datas: List[schemas.C2db], db: Session = Depends(get_db)):
    return crud.createC2db(db, datas)


@router.get("/queryC2db", response_model=List[schemas.C2db])
def queryC2db(query=Depends(depends.queryC2db)):
    return query
