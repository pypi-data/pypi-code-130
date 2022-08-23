from termcolor import colored
from functools import reduce
from typing import List
from model.common.address import Address
from model.common.phone import Phone
from model.common.trperson import (
    COR,
    PersonId,
    Personal,
    Marriage,
    Education,
    Employment,
)
import json

from model.common.tr import TrCaseIn, TrBackground, SpInCanada
from model.common.commonmodel import CommonModel, BuilderModel
from pdfform.tr.fb5709 import FormBuilder5709
from pydantic import BaseModel


class M5709Model(BaseModel, BuilderModel):
    personal: Personal
    marriage: Marriage
    personid: List[PersonId]
    address: List[Address]
    education: List[Education]
    employment: List[Employment]
    phone: List[Phone]
    cor: List[COR]
    trcasein: TrCaseIn
    spincanada: SpInCanada
    trbackground: TrBackground

    def make_pdf_form(self, output_json, *args, **kwargs):
        pf = FormBuilder5709(self)
        form = pf.get_form()
        with open(output_json, "w") as output:
            json.dump(form.actions, output, indent=3, default=str)
        print(colored(f"{output_json} has been created. ", "green"))

    def make_web_form(self, output_json, upload_dir, rcic, *args, **kwargs):
        raise ValueError("This model doesn't have webform...")

    def context(self, *args, **kwargs):
        raise ValueError("This model doesn't have webform...")
