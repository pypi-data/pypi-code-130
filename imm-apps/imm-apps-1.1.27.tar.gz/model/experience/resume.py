from .context import DATADIR
from email.policy import default
from textwrap import indent
from typing import List, Optional
from model.experience.resumedata import (
    Personal,
    Language,
    PersonalAssess,
    Education,
    Employment,
)
from model.common.commonmodel import CommonModel
from model.common.phone import Phone, Phones
from model.common.address import Address, Addresses
from pydantic import BaseModel


class ResumeModel(BaseModel):
    personal: Personal
    phone: List[Phone]
    personalassess: PersonalAssess
    education: List[Education]
    language: Optional[List[Language]]
    employment: Optional[List[Employment]]
    address: List[Address]

    def context(self, doc_type=None):
        return {
            **self.dict(),
            "phone": Phones(self.phone).PreferredPhone.international_format_full,
            "address": Addresses(self.address).PreferredAddress.full_address,
            "full_name": self.personal.full_name,
        }
