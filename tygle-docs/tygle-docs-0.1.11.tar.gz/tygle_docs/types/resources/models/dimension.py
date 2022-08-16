from pydantic import BaseModel, Field
from tygle_docs.types.enums import Unit


class Dimension(BaseModel):
    magnitude: int = Field()
    unit: Unit = Field()
