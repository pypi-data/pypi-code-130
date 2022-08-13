from typing import Union

from pydantic import BaseModel


class Ribbon(BaseModel):
    id: str
    formula: Union[str, None] = None
    work_path: Union[str, None] = None
    description: Union[str, None] = None
    poscar: Union[str, None] = None
    contcar: Union[str, None] = None
    last_step_energy: Union[float, None] = None
    E0: Union[float, None] = None
    mag: Union[float, None] = None
    vacuum_level: Union[float, None] = None
    e_fermi: Union[float, None] = None
    band_gap: Union[float, None] = None
    vbm_: Union[float, None] = None
    cbm_: Union[float, None] = None
    fermi_energy: Union[float, None] = None
    work_function: Union[float, None] = None
    vbm_position: Union[str, None] = None
    cbm_position: Union[str, None] = None
    cbm: Union[float, None] = None
    vbm: Union[float, None] = None
    c2db_ID: Union[int, None] = None
    c2db_BandGap_HSE_minus_PBE: Union[float, None] = None
    info: Union[str, None] = None
    hse_band_gap_predicted: Union[float, None] = None

    class Config:
        orm_mode = True


class RibbonQuery(BaseModel):
    id: Union[str, None] = None,
    c2db_ID: Union[int, None] = None,
    skip: int = 0,
    limit: int = 100,
    description: Union[int, None] = None,
    work_path: Union[str, None] = None,
    min_last_step_energy: Union[float, None] = None,
    min_E0: Union[float, None] = None,
    min_mag: Union[float, None] = None,
    min_vacuum_level: Union[float, None] = None,
    min_e_fermi: Union[float, None] = None,
    min_band_gap: Union[float, None] = None,
    min_fermi_energy: Union[float, None] = None,
    min_work_function: Union[float, None] = None,
    min_cbm: Union[float, None] = None,
    min_vbm: Union[float, None] = None,
    max_last_step_energy: Union[float, None] = None,
    max_E0: Union[float, None] = None,
    max_mag: Union[float, None] = None,
    max_vacuum_level: Union[float, None] = None,
    max_e_fermi: Union[float, None] = None,
    max_band_gap: Union[float, None] = None,
    max_fermi_energy: Union[float, None] = None,
    max_work_function: Union[float, None] = None,
    max_cbm: Union[float, None] = None,
    max_vbm: Union[float, None] = None,
    min_hse_band_gap_predicted: Union[float, None] = None
    max_hse_band_gap_predicted: Union[float, None] = None


class RibbonRunStatusResponse(BaseModel):
    isRunning: bool
    code: int
    status: str


class RibbonInfo(BaseModel):
    username: str
    password: str
    filepath: str
    isHSECalc: Union[bool, None] = None
    HSE_calc_path: Union[str, None] = None
    isRunning: Union[bool, None] = None
    ip: str


class RibbonInfos(BaseModel):
    id: str
    info: RibbonInfo


class RibbonInfoUpdateResponse(BaseModel):
    id: str
    status: str
    code: int


class RibbonInfoResponse(BaseModel):
    id: str
    info: RibbonInfo


class RibbonResponseModel(BaseModel):
    id: str
    status: str
    code: int
    formula: Union[str, None] = None

    class Config:
        orm_mode = True
