from .context import DATADIR
from typing import List
from model.common.commonmodel import CommonModel, BuilderModel
from model.lmia.data import LmiaCase, Contact, General
from model.common.advertisement import (
    Advertisement,
    InterviewRecord,
    InterviewRecords,
    Advertisements,
)
from model.common.person import Person
from model.common.contact import Contacts
from model.common.jobofferbase import JobofferBase
import os
from model.common.wordmaker import WordMaker
from model.recruit.recruitmentsummary import (
    RecruitmnetSummaryModel,
    General,
    Contact,
    LmiaCase,
    Advertisement,
    InterviewRecord,
    Joboffer,
    Personal,
)


class RecruitmnetSummaryModelE(CommonModel, RecruitmnetSummaryModel):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/recruitment.xlsx", "excel/lmia.xlsx", "excel/er.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())


class RecruitmnetSummaryDocxAdaptor:
    def __init__(self, recruitment_summary_obj: RecruitmnetSummaryModel):
        self.recruitment_summary_obj = recruitment_summary_obj

    def re_generate_dict(self):
        summary_info = {
            "resume_num": self.recruitment_summary_obj.summary.resume_num,
            "canadian_num": self.recruitment_summary_obj.summary.canadian_num,
            "unknown_num": self.recruitment_summary_obj.summary.unknown_num,
            "foreigner_num": self.recruitment_summary_obj.summary.foreigner_num,
            "total_canadian": self.recruitment_summary_obj.summary.total_canadian,
            "total_interviewed_canadians": self.recruitment_summary_obj.summary.total_interviewed_canadians,
            "canadian_records": self.recruitment_summary_obj.summary.canadian_records,
            "contact": self.recruitment_summary_obj.selected_contact,
            "advertisement": self.recruitment_summary_obj.advertisements,
        }
        return {**self.recruitment_summary_obj.dict(), **summary_info}

    def make(self, output_docx, template_no=None):
        template_path = os.path.abspath(
            os.path.join(DATADIR, "word/lmia_recruitment_summary.docx")
        )
        wm = WordMaker(template_path, self.re_generate_dict(), output_docx)
        wm.make()
