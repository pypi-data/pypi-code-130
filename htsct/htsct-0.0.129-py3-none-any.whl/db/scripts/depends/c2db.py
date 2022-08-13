from typing import Union

from fastapi import Depends
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db


def queryC2db(
        db: Session = Depends(get_db),
        id: Union[str, None] = None,
        skip: int = 0,
        limit: int = 100,
        min_band_gap: Union[str, None] = None,
        max_band_gap: Union[str, None] = None):
    return crud.queryC2db(db, id, skip, limit, min_band_gap, max_band_gap)
