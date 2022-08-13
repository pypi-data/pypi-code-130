from typing import Union

from pydantic import BaseModel


class Config(BaseModel):
    id: str
    vasp_std: Union[str, None] = None
    vasp_ncl: Union[str, None] = None
    vasp_gam: Union[str, None] = None
    vasp_inputs: Union[str, None] = None
    qsub: Union[str, None] = None
    qsub_filename: Union[str, None] = None
    work_path: Union[str, None] = None
    wait_interval: Union[int, None] = None
    input_file_type: Union[str, None] = None

    class Config:
        orm_mode = True


class FullConfig(Config):
    active: bool
