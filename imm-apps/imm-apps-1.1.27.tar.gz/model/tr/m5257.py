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
from pydantic import BaseModel

"""
Program model for temporary resident visa. Get and validate info for forms: imm5257, imm0104, imm5257b_1, and imm5645
"""


class M5257Model(BaseModel):
    personal: Personal
    marriage: Marriage
    personid: List[PersonId]
    address: List[Address]
    education: List[Education]
    employment: List[Employment]
    travel: List[Travel]
    family: List[Family]
    phone: List[Phone]
    cor: List[COR]
    trcase: TrCase
    visa: Visa
    trbackground: TrBackground
