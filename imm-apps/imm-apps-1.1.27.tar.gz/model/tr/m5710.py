from typing import List, Optional
from model.common.address import Address
from model.common.phone import Phone
from model.common.trperson import (
    COR,
    PersonId,
    Personal,
    Marriage,
    Education,
    Employment,
    # Family,
)
from model.common.tr import TrCaseIn, TrBackground, WpInCanada
from model.common.commonmodel import CommonModel, BuilderModel
from pdfform.tr.fb5710 import FormBuilder5710
from termcolor import colored
import json
from pydantic import BaseModel


class M5710Model(BaseModel, BuilderModel):
    personal: Personal
    marriage: Marriage
    personid: List[PersonId]
    address: List[Address]
    education: List[Education]
    employment: List[Employment]
    phone: List[Phone]
    cor: List[COR]
    trcasein: TrCaseIn
    wpincanada: WpInCanada
    trbackground: TrBackground

    def make_pdf_form(self, output_json, *args, **kwargs):
        pf = FormBuilder5710(self)
        form = pf.get_form()
        with open(output_json, "w") as output:
            json.dump(form.actions, output, indent=3, default=str)
        print(colored(f"{output_json} has been created. ", "green"))

    def make_web_form(self, output_json, upload_dir, rcic, *args, **kwargs):
        raise ValueError("This model doesn't have webform...")

    def context(self, *args, **kwargs):
        raise ValueError("This model doesn't have webform...")
