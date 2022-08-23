from datetime import date
from typing import Optional, List
from pydantic import BaseModel, root_validator, EmailStr
from model.common.commonmodel import CommonModel
from model.common.address import Address
from model.common.contact import ContactBase
from termcolor import colored
from model.common.jobposition import PositionBase
from model.common.jobofferbase import JobofferBase
from model.common.person import Person, PersonalAssess
from model.lmia.rcic import LmiaRcic, LmiaCase, Position, Joboffer, Lmi


class LmiaRcicE(CommonModel, LmiaRcic):
    lmiacase: LmiaCase
    position: Position
    joboffer: Joboffer
    lmi: Lmi
    personalassess: PersonalAssess

    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/er.xlsx", "excel/lmia.xlsx", "excel/pa.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
