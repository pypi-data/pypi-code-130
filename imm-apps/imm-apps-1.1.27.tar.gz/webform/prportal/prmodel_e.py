from termcolor import colored
from utils.utils import checkContinuity
from typing import List, Optional, Union
from model.common.address import Address
from model.common.educationbase import EducationBase
from model.common.phone import Phone
from model.common.commonmodel import CommonModel
from model.common.id import ID
from model.common.person import Person
from datetime import date
from pydantic import BaseModel, EmailStr, root_validator, validator
from model.common.utils import normalize
from webform.prportal.data.country import country_residence
from model.common.mixins import DatePeriod
from webform.prportal.prmodel import (
    PrModel,
    Personal,
    Status,
    COR,
    Marriage,
    Phone,
    PersonId,
    PRCase,
    Family,
    Travel,
    PRBackground,
    Education,
    History,
    Member,
    Government,
    Military,
    AddressHistory,
)


class PrModelE(CommonModel, PrModel):
    personal: Personal

    def __init__(self, excels=None, output_excel_file=None, check=True):
        mother_excels = ["excel/pr.xlsx", "excel/pa.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
