from .context import DATADIR
from typing import List
from model.common.commonmodel import CommonModel
from model.bcpnp.data import Contact, General, JobOffer, PersonalAssess, Bcpnp
from model.common.jobposition import PositionBase
from model.common.person import Person
from model.common.advertisement import (
    Advertisement,
    Advertisements,
    InterviewRecord,
    RecruitmentSummary,
    InterviewRecords,
)
from model.common.contact import Contacts
from model.common.wordmaker import WordMaker
import os
from model.bcpnp.recommendationletter import (
    RecommendationLetterModel,
    Personal,
    Position,
)


class RecommendationLetterModelE(CommonModel, RecommendationLetterModel):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = [
            "excel/er.xlsx",
            "excel/pa.xlsx",
            "excel/recruitment.xlsx",
            "excel/bcpnp.xlsx",
            "excel/rep.xlsx",
        ]
        super().__init__(excels, output_excel_file, mother_excels, globals())
