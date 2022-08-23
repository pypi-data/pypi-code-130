from datetime import date
from typing import Optional, List
from pydantic import BaseModel, root_validator
from model.common.commonmodel import CommonModel
from model.lmia.stage1 import LmiaAssess, General, Employee_list, Lmi


class LmiaAssessE(CommonModel):
    general: General
    employee_list: List[Employee_list]
    lmi: Lmi

    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/er.xlsx", "excel/lmia.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
