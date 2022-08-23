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
from model.bcpnp.mrep import MRepModel, General, Contact, Personal


class MRepModelE(CommonModel, MRepModel):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/pa.xlsx", "excel/rep.xlsx", "excel/er.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
