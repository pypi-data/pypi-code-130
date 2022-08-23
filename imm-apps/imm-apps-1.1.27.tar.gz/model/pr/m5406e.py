from pydantic import BaseModel, EmailStr, root_validator
from typing import Optional, List
from datetime import date

from model.common.commonmodel import CommonModel
from model.pr.m5406 import M5406Model, Family


class M5406ModelE(CommonModel, M5406Model):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/pa.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
