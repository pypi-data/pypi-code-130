from termcolor import colored
from functools import reduce
from typing import List, Optional
from model.common.address import Address
from ..common.educationbase import EducationHistory
from model.common.phone import Phone
from model.common.trperson import (
    COR,
    PersonId,
    Personal,
    Marriage,
    Education,
    Employment,
    Travel,
    Family,
)
from model.common.person import PersonalAssess
from model.common.tr import TrCase, Wp, TrBackground
from model.common.commonmodel import CommonModel, BuilderModel
from pdfform.tr.fb1295 import FormBuilder1295
from model.lmia.common import Rcic
import json
from pydantic import BaseModel


class M1295Model(BaseModel, BuilderModel):
    personal: Personal
    personalassess: PersonalAssess
    marriage: Marriage
    personid: List[PersonId]
    address: List[Address]
    education: List[Education]
    employment: List[Employment]
    travel: List[Travel]
    family: List[Family]
    phone: List[Phone]
    cor: List[COR]
    trcase: TrCase
    wp: Wp
    trbackground: TrBackground
    rcic: Rcic

    def make_pdf_form(self, output_json, *args, **kwargs):
        pf = FormBuilder1295(self)
        form = pf.get_form()
        with open(output_json, "w") as output:
            json.dump(form.actions, output, indent=3, default=str)
        print(colored(f"{output_json} has been created. ", "green"))

    def make_web_form(self, output_json, upload_dir, rcic, *args, **kwargs):
        raise ValueError("This model doesn't have webform...")

    def context(self, *args, **kwargs):
        education = EducationHistory(self.education)
        educations = (
            education.post_secondary
            if len(education.post_secondary) > 0
            else education.high_school
        )
        return {
            **self.dict(),
            "birthday": self.personal.birthday,
            "respectful_full_name": self.personal.respectful_full_name,
            "short_name": self.personal.short_name,
            "educations": educations,
            "ties": [self.wp.family_tie, self.wp.economic_tie, self.wp.other_tie],
        }
