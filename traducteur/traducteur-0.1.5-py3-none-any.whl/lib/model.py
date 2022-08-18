from pydantic import BaseModel as BasePydanticModel
from datetime import datetime
from typing import Optional, Any

class BaseModel(BasePydanticModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    @property
    def column_names(self):
        return [str(col).lower() for col in self.dict().keys()]

    @property
    def column_values(self):
        return tuple([str(v) for v in self.dict().values()])

    def __init__(__pydantic_self__, **data: Any):
        super().__init__(**data)

    def save(self):
        pass

    def delete(self):
        pass

    @classmethod
    def get(cls, id: str):
        pass

    @classmethod
    def get_where(cls, query):
        pass

    @classmethod
    def exists(cls, id):
        pass

    @classmethod
    def exists_where(cls, query):
        pass


class BaseSQLModel(BaseModel):
    @property
    def sql_columns(self):
        return ', '.join(self.column_names)

    @property
    def sql_values(self):
        return ', '.join(self.column_values)

    @property
    def q_marks(self):
        return ', '.join(['?' for _ in range(len(self.column_names))])

    @property
    def sql_update(self):
        return ', '.join([f"{str(col).lower()} = {val}" for col, val in self.dict().items()])