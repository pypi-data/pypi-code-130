from sqlalchemy import String, Column, Float, Integer

from ..database import DB

Base = DB.Base


class Ribbon(Base):
    __tablename__ = "ribbon"
    id = Column(String(length=50), primary_key=True, unique=True, index=True)
    formula = Column(String(length=50))
    work_path = Column(String(length=100))
    description = Column(String)
    poscar = Column(String)
    contcar = Column(String)
    last_step_energy = Column(Float)
    E0 = Column(Float)
    mag = Column(Float)
    vacuum_level = Column(Float)
    e_fermi = Column(Float)
    band_gap = Column(Float)
    vbm_ = Column(Float)
    cbm_ = Column(Float)
    fermi_energy = Column(Float)
    work_function = Column(Float)
    vbm_position = Column(String)
    cbm_position = Column(String)
    cbm = Column(Float)
    vbm = Column(Float)
    c2db_ID = Column(Integer)
    c2db_BandGap_HSE_minus_PBE = Column(Float)
    info = Column(String)
    hse_band_gap_predicted = Column(Float)
