from typing import List, Union

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(
    tags=["vaspInput"],
)


@router.get("/queryVaspInput", response_model=List[schemas.VaspInputJson])
def queryVaspInput(name: Union[str, None] = None, skip: int = 0, limit: int = 2, db: Session = Depends(get_db)):
    return crud.queryVaspInput(db, name, skip, limit)


@router.post("/createVaspInput", response_model=schemas.VaspInputResponseModel)
def createVaspInput(inputs: schemas.VaspInput, db: Session = Depends(get_db)):
    return crud.createVaspInput(db, inputs)


@router.delete("/deleteVaspInput", response_model=schemas.VaspInputResponseModel)
def deleteVaspInput(name: str, db: Session = Depends(get_db)):
    return crud.deleteVaspInput(db, name)


@router.put("/updateVaspInput", response_model=List[schemas.VaspInputResponseModel])
def updateVaspInput(inputs: List[schemas.VaspInput], db: Session = Depends(get_db)):
    return crud.updateVaspInput(db, inputs)
