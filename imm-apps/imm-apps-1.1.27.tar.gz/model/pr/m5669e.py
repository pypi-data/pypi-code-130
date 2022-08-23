from termcolor import colored
from pydantic import BaseModel, EmailStr, root_validator
from functools import reduce
from typing import List, Optional
from model.common.address import Address
from model.common.mixins import DatePeriod
from model.common.phone import Phone
from model.common.commonmodel import CommonModel
from model.common.educationbase import EducationBase
from model.common.utils import checkRow
from utils.utils import checkContinuity
from datetime import date
from pprint import pprint
from model.pr.m5669 import (
    M5669Model,
    Personal,
    Family,
    PRBackground,
    Education,
    History,
    Member,
    Government,
    Military,
    AddressHistory,
)


class M5669ModelE(CommonModel, M5669Model):
    def __init__(self, excels=None, output_excel_file=None, check=False):
        mother_excels = ["excel/pr.xlsx", "excel/pa.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
        if check:
            [self.check(item) for item in [self.history, self.addresshistory]]

    def check(self, items: List[object]):
        results = []
        # construct list suitable for checkContinuity
        for item in items:
            results.append(list(item.__dict__.values()))

        # check
        continued, sorted_list, msg = checkContinuity(results)

        if not continued:
            print(
                colored(
                    f"There are {len(msg)} error(s) in sheet {items[0].__str__}", "red"
                )
            )
            [print(index, "\t", m) for index, m in enumerate(msg)]
