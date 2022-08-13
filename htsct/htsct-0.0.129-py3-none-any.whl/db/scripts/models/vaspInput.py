from sqlalchemy import String, Column

from ..database import DB

Base = DB.Base


class VaspInput(Base):
    __tablename__ = "vasp_input"
    name = Column("name", String, primary_key=True, unique=True, index=True)
    inputs = Column("inputs", String)
