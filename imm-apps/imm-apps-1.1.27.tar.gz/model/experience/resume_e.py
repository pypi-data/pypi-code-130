from .context import DATADIR
from email.policy import default
from textwrap import indent
from typing import List, Optional
from model.experience.resumedata import (
    Personal,
    Language,
    PersonalAssess,
    Education,
    Employment,
)
from model.common.commonmodel import CommonModel
from model.common.phone import Phone, Phones
from model.common.address import Address, Addresses
from model.experience.resume import ResumeModel


class ResumeModelE(CommonModel, ResumeModel):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/pa.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
