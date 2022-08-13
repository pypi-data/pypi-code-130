from pydantic import BaseModel, HttpUrl


class RedirectIn(BaseModel):
    path: str
    target: HttpUrl
    is_custom: bool = False


class Redirect(BaseModel):
    id: int
    path: str
    target: HttpUrl
    is_custom: bool

    class Config:
        orm_mode = True
