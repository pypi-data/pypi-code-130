from .context import DATADIR
from typing import List

from pydantic import EmailStr
from model.common.commonmodel import CommonModel
from model.bcpnp.data import Bcpnp, General, JobOffer, ErAddress
from model.common.jobposition import PositionBase
from model.common.rcic import Rcic
from model.common.advertisement import Advertisement, Advertisements, RecruitmentSummary
from model.common.person import Person, PersonalAssess
from model.common.address import Address, Addresses
from model.common.phone import Phone, Phones
from model.common.wordmaker import WordMaker
import os
from model.bcpnp.employeetraining import EmployeeTrainingModel, Personal, Position


class EmployeeTrainingModelE(CommonModel, EmployeeTrainingModel):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = [
            "excel/er.xlsx",
            "excel/pa.xlsx",
            "excel/recruitment.xlsx",
            "excel/bcpnp.xlsx",
            "excel/rep.xlsx",
        ]
        super().__init__(excels, output_excel_file, mother_excels, globals())
