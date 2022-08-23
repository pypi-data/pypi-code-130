from termcolor import colored
from functools import reduce
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
    Travel,
    Family,
)
from model.common.tr import TrCase, Visa, TrBackground
from model.common.commonmodel import CommonModel
from model.tr.m5257 import M5257Model

"""
Program model for temporary resident visa. Get and validate info for forms: imm5257, imm0104, imm5257b_1, and imm5645
"""


class M5257ModelE(CommonModel, M5257Model):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/tr.xlsx", "excel/pa.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
