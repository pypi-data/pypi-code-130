from pydantic import BaseModel


class VaspInput(BaseModel):
    name: str
    inputs: str

    class Config:
        orm_mode = True


class VaspInputJson(BaseModel):
    name: str
    inputs: dict


class VaspInputResponseModel(BaseModel):
    name: str
    status: str
    code: int
