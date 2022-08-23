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
from pydantic import BaseModel


class Personal(Person):
    def __str__(self):
        return self.full_name


class Joboffer(JobofferBase):
    pass


class RecruitmnetSummaryModel(BaseModel, BuilderModel):
    general: General
    contact: List[Contact]
    lmiacase: LmiaCase
    advertisement: List[Advertisement]
    interviewrecord: List[InterviewRecord]
    joboffer: Joboffer

    @property
    def selected_contact(self):
        contacts = Contacts(self.contact)
        return contacts.preferredContact

    @property
    def summary(self):
        return InterviewRecords(self.interviewrecord)

    @property
    def advertisements(self):
        records = []
        i = 1
        for adv in self.advertisement:
            records.append({**{"days": adv.days}, **adv.dict()})
            i += 1
        return records

    def context(self, *args, **kwargs):
        interview = InterviewRecords(self.interviewrecord)
        primary_contact = Contacts(self.contact).primary
        return {
            **self.dict(),
            "num_of_job_posts": Advertisements(self.advertisement).amount,
            "adv_summary": [
                {
                    "start_date": a.start_date,
                    "end_date": a.end_date,
                    "media": a.media,
                    "days": a.days,
                }
                for a in self.advertisement
            ],
            "high_wage": True
            if float(self.joboffer.hourly_rate) >= self.lmiacase.provincial_median_wage
            else False,
            "rs": {
                "resume_num": interview.resume_num,
                "canadian_num": interview.canadian_num,
                "unknown_num": interview.unknown_num,
                "foreigner_num": interview.foreigner_num,
                "total_canadian": interview.total_canadian,
                "total_interviewed_canadians": interview.total_interviewed_canadians,
                "canadian_records": interview.canadian_records,
            },
            "primary_contact": primary_contact,
        }

    def make_pdf_form(self, *args, **kwargs):
        pass

    def make_web_form(self, *args, **kwargs):
        pass


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
