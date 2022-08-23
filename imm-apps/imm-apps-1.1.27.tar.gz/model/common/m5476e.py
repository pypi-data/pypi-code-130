from datetime import date
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date
from model.common.commonmodel import CommonModel, BuilderModel
from model.common.rcic import RcicList
from pdfform.common.fb5476 import FormBuilder5476
import json
from termcolor import colored
from model.common.m5476 import M5476Model, Personal, RcicList


class M5476ModelE(CommonModel, M5476Model):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = [
            "excel/pa.xlsx",
            "excel/rep.xlsx",
        ]
        super().__init__(excels, output_excel_file, mother_excels, globals())
