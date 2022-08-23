from datetime import date
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date
from model.common.commonmodel import CommonModel, BuilderModel
from model.common.rcic import RcicList
from model.common.contact import ContactBase
from pdfform.bcpnp.fbrep import FormBuilderBcRep
import json
from termcolor import colored
from model.common.employerbase import EmployerBase
from webform.bcpnp.rep import Representative


class General(EmployerBase):
    pass


class Contact(ContactBase):
    pass


class Personal(BaseModel):
    last_name: str
    first_name: str
    sex: str
    dob: date
    uci: Optional[str]


class MRepModel(BaseModel, BuilderModel):
    rciclist: List[RcicList]
    personal: Personal
    general: General
    contact: List[Contact]

    def make_pdf_form(self, output_json, rcic_id_name, *args, **kwargs):
        pf = FormBuilderBcRep(self, rcic_id_name)
        form = pf.get_form()
        with open(output_json, "w") as output:
            json.dump(form.actions, output, indent=3, default=str)
        print(colored(f"{output_json} has been created. ", "green"))

    def make_web_form(self, output_json, upload_dir, rcic_id_name, *args, **kwargs):
        # actions = Representative(self, rcic_id_name).fill()
        # with open(output_json, "w") as output:
        #     json.dump(actions, output, indent=3, default=str)
        # print(colored(f"{output_json} has been created. ", "green"))
        raise ValueError("This model doesn't have webform...")

    def context(self, *args, **kwargs):
        raise ValueError("This model doesn't have webform...")
