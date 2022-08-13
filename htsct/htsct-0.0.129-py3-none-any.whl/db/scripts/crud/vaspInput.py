from typing import List, Union

import json
from fastapi import status
from sqlalchemy.orm import Session, Query
from .. import models
from .. import schemas


##################
### vasp input ###
##################
def createVaspInput(db: Session, inputs: schemas.VaspInput):
    vaspInputs = models.VaspInput(**inputs.dict(exclude_unset=True))
    print(vaspInputs)
    if not db.query(models.VaspInput).filter(models.VaspInput.name == inputs.name).first():
        db.add(vaspInputs)
        db.commit()
        return {"status": "创建成功", "name": vaspInputs.name, "code": status.HTTP_201_CREATED}
    else:
        return {"status": "记录已存在，请勿重复创建", "name": vaspInputs.name, "code": status.HTTP_202_ACCEPTED}


def queryVaspInput(db: Session, name: Union[str, None] = None, skip: int = 0, limit: int = 2, ):
    db_query: Union[Query, None] = db.query(models.VaspInput)
    if name:
        db_query = db_query.filter(models.VaspInput.name == name)
    vaspInputs = db_query.offset(skip).limit(limit).all()
    return [{"name": vaspInput.name, "inputs": json.loads(vaspInput.inputs)} for vaspInput in vaspInputs]


def deleteVaspInput(db: Session, name: str):
    input_ = db.query(models.VaspInput).filter(models.VaspInput.name == name).first()
    if input_:
        db.query(models.VaspInput).filter(models.VaspInput.name == name).delete()
        db.commit()
        return {"status": "删除成功", "name": input_.name, "code": status.HTTP_200_OK}
    return {"status": "记录不存在", "name": None, "code": status.HTTP_200_OK}


def updateVaspInput(db: Session, inputs: List[schemas.VaspInput]):
    response = []
    for input_ in inputs:
        if not db.query(models.VaspInput).filter(models.VaspInput.name == input_.name).first():
            response.append(
                {"status": "记录不存在，请新建", "name": input_.name, "code": status.HTTP_404_NOT_FOUND})
            continue
        db.query(models.VaspInput).filter(models.VaspInput.name == input_.name).update(input_.dict(exclude_unset=True))
        response.append(
            {"status": "update succeed", "name": input_.name, "code": status.HTTP_200_OK})
    db.commit()
    return response
