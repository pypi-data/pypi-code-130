from model.common.commonmodel import CommonModel
from datetime import date
from pydantic import BaseModel, root_validator
from typing import List
from model.common.mixins import DatePeriod
from model.common.utils import checkRow
from model.pr.m5562 import M5562Model, Travel, Personal


class M5562ModelE(CommonModel, M5562Model):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/pa.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
