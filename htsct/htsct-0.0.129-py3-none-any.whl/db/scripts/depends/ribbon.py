from typing import Union
from fastapi import Depends
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db


def queryRibbons(
        id: Union[str, None] = None,
        c2db_ID: Union[int, None] = None,
        skip: int = 0,
        limit: int = 100,
        work_path: Union[str, None] = None,
        description: Union[str, None] = None,
        min_last_step_energy: Union[float, None] = None,
        max_last_step_energy: Union[float, None] = None,
        min_E0: Union[float, None] = None,
        max_E0: Union[float, None] = None,
        min_mag: Union[float, None] = None,
        max_mag: Union[float, None] = None,
        min_vacuum_level: Union[float, None] = None,
        max_vacuum_level: Union[float, None] = None,
        min_e_fermi: Union[float, None] = None,
        max_e_fermi: Union[float, None] = None,
        min_band_gap: Union[float, None] = None,
        max_band_gap: Union[float, None] = None,
        min_fermi_energy: Union[float, None] = None,
        max_fermi_energy: Union[float, None] = None,
        min_work_function: Union[float, None] = None,
        max_work_function: Union[float, None] = None,
        min_cbm: Union[float, None] = None,
        max_cbm: Union[float, None] = None,
        min_vbm: Union[float, None] = None,
        max_vbm: Union[float, None] = None,
        min_hse_band_gap_predicted: Union[float, None] = None,
        max_hse_band_gap_predicted: Union[float, None] = None,
        db: Session = Depends(get_db)):
    return crud.queryRibbon(db, id=id, c2db_ID=c2db_ID, skip=skip, limit=limit, work_path=work_path,
                            description=description,
                            min_last_step_energy=min_last_step_energy, min_E0=min_E0, min_mag=min_mag,
                            min_vacuum_level=min_vacuum_level, min_e_fermi=min_e_fermi, min_band_gap=min_band_gap,
                            min_fermi_energy=min_fermi_energy, min_work_function=min_work_function, min_cbm=min_cbm,
                            min_vbm=min_vbm, max_last_step_energy=max_last_step_energy, max_E0=max_E0, max_mag=max_mag,
                            max_vacuum_level=max_vacuum_level, max_e_fermi=max_e_fermi, max_band_gap=max_band_gap,
                            max_fermi_energy=max_fermi_energy, max_work_function=max_work_function, max_cbm=max_cbm,
                            max_vbm=max_vbm, min_hse_band_gap_predicted=min_hse_band_gap_predicted,
                            max_hse_band_gap_predicted=max_hse_band_gap_predicted)
