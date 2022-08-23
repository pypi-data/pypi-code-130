from datetime import date
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date
from model.common.commonmodel import CommonModel, BuilderModel
from model.common.rcic import RcicList
from pdfform.common.fb5476 import FormBuilder5476
import json
from termcolor import colored


class Personal(BaseModel):
    last_name: str
    first_name: str
    sex: str
    dob: date
    uci: Optional[str]


class M5476Model(BaseModel, BuilderModel):
    rciclist: List[RcicList]
    personal: Personal

    def make_pdf_form(self, output_json, rcic_id_name, *args, **kwargs):
        pf = FormBuilder5476(self, rcic_id_name)
        form = pf.get_form()
        with open(output_json, "w") as output:
            json.dump(form.actions, output, indent=3, default=str)
        print(colored(f"{output_json} has been created. ", "green"))

    def make_web_form(self, output_json, upload_dir, rcic, *args, **kwargs):
        raise ValueError("This model doesn't have webform...")

    def context(self, *args, **kwargs):
        raise ValueError("This model doesn't have webform...")
