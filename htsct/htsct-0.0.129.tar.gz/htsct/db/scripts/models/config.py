from sqlalchemy import String, Column, Integer, Boolean

from ..database import DB

Base = DB.Base


class Config(Base):
    __tablename__ = "config"
    id = Column("id", String, primary_key=True, unique=True, index=True)
    vasp_std = Column("vasp_std", String)
    vasp_ncl = Column("vasp_ncl", String)
    vasp_gam = Column("vasp_gam", String)
    vasp_inputs = Column("vasp_inputs", String)
    qsub = Column("qsub", String)
    qsub_filename = Column("qsub_filepath", String)
    work_path = Column("work_path", String)
    wait_interval = Column("wait_interval", Integer)
    input_file_type = Column("input_file_type", String)
    active = Column("active", Boolean)
