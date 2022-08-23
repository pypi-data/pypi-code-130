from typing import List, Optional, Union
from model.common.address import Address
from model.common.educationbase import EducationBase
from model.common.phone import Phone
from model.common.commonmodel import CommonModel
from model.common.id import ID
from datetime import date
from pydantic import BaseModel, EmailStr, root_validator, validator
from model.common.utils import normalize
from model.common.mixins import DatePeriod
from termcolor import colored
from model.pr.m0008 import (
    M0008Model,
    Personal,
    Status,
    COR,
    Marriage,
    Address,
    Phone,
    PersonId,
    Education,
    PRCase,
)


class M0008ModelE(CommonModel, M0008Model):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/pr.xlsx", "excel/pa.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
