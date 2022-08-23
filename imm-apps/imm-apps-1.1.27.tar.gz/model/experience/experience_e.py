from pathlib import Path
from model.experience.data import (
    Employment,
    Personal,
    Language,
    PersonalAssess,
    Education,
)
from model.common.employmenthistory import EmploymentHistory
from model.common.id import ID, IDs
from typing import List, Optional
from model.common.commonmodel import CommonModel, BuilderModel
from model.common.phone import Phone, Phones
from model.common.address import Address, Addresses
from model.experience.experience import ExperienceModel


class PersonId(ID):
    pass


DATADIR = Path(__file__).parents[2] / "data"


class ExperienceModelE(CommonModel, ExperienceModel):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/pa.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
