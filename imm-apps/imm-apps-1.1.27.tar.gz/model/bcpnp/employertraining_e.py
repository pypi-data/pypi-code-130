from .context import DATADIR
from typing import List
from model.common.commonmodel import CommonModel, BuilderModel
from model.bcpnp.data import Bcpnp, General, JobOffer, ErAddress
from model.common.jobposition import PositionBase
from model.common.rcic import Rcic
from model.common.advertisement import (
    Advertisement,
    Advertisements,
    InterviewRecord,
    InterviewRecords,
    RecruitmentSummary,
)
from model.common.person import Person, PersonalAssess
from model.common.address import Addresses
from model.common.wordmaker import WordMaker
import os
from model.bcpnp.employertraining import (
    EmployerTrainingModel,
    ErAddress,
    General,
    Position,
    Personal,
    JobOffer,
    PersonalAssess,
    Bcpnp,
    Rcic,
    Advertisement,
    InterviewRecord,
    RecruitmentSummary,
)


class EmployerTrainingModelE(CommonModel, EmployerTrainingModel):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = [
            "excel/er.xlsx",
            "excel/pa.xlsx",
            "excel/recruitment.xlsx",
            "excel/bcpnp.xlsx",
            "excel/rep.xlsx",
        ]
        super().__init__(excels, output_excel_file, mother_excels, globals())
