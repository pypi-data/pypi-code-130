from datetime import date
from typing import Optional, List
from pydantic import BaseModel, root_validator, EmailStr
from model.common.commonmodel import CommonModel
from model.common.address import Address
from model.common.contact import ContactBase
from model.common.mediaaccount import MediaAccount
from termcolor import colored
from model.common.jobposition import PositionBase
from model.common.jobofferbase import JobofferBase
from model.common.person import Person
from model.lmia.stage2 import (
    LmiaRecruitment,
    General,
    ErAddress,
    Contact,
    Finance,
    Joboffer,
    Lmi,
    Personal,
    Position,
)


class LmiaRecruitmentE(CommonModel):
    general: General
    personal: Personal
    position: Position
    eraddress: List[ErAddress]
    contact: List[Contact]
    finance: List[Finance]
    joboffer: Joboffer
    lmi: Lmi
    address: List[Address]
    mediaaccount: List[MediaAccount]

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None):

        mother_excels = ["excel/er.xlsx", "excel/lmia.xlsx", "excel/pa.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
