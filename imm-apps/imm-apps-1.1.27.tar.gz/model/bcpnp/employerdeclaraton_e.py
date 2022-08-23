from typing import List
from model.common.commonmodel import CommonModel, BuilderModel
from model.bcpnp.data import Bcpnp, Contact, General, JobOffer, ErAddress
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
from model.common.contact import Contacts
from model.common.address import Addresses
from model.common.phone import Phone, Phones
from datetime import date
from model.common.xmlfiller import XmlFiller
import os
from typing import Optional
from pdfform.bcpnp.fbemployerdeclaration import FormBuilderEmployerDeclaration
from model.bcpnp.employerdeclaraton import (
    EmployerDeclaratonFormModel,
    Personal,
    Position,
)


class EmployerDeclaratonFormModelE(CommonModel, EmployerDeclaratonFormModel):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = [
            "excel/er.xlsx",
            "excel/pa.xlsx",
            "excel/recruitment.xlsx",
            "excel/bcpnp.xlsx",
            "excel/rep.xlsx",
        ]
        super().__init__(excels, output_excel_file, mother_excels, globals())
