from .context import DATADIR
from typing import List

from pydantic import EmailStr, BaseModel
from model.common.commonmodel import CommonModel
from model.bcpnp.data import Bcpnp, General, JobOffer, ErAddress
from model.common.jobposition import PositionBase
from model.common.rcic import Rcic
from model.common.advertisement import Advertisement, Advertisements, RecruitmentSummary
from model.common.person import Person, PersonalAssess
from model.common.address import Address, Addresses
from model.common.phone import Phone, Phones
from model.common.wordmaker import WordMaker
import os
from model.common.commonmodel import CommonModel, BuilderModel


class Personal(Person):
    email: EmailStr

    def __str__(self):
        return self.full_name


class Position(PositionBase):
    pass


class EmployeeTrainingModel(BaseModel, BuilderModel):
    eraddress: List[ErAddress]
    general: General
    position: Position
    personal: Personal
    phone: List[Phone]
    address: List[Address]
    joboffer: JobOffer
    personalassess: PersonalAssess
    bcpnp: Bcpnp
    rcic: Rcic
    advertisement: List[Advertisement]
    recruitmentsummary: RecruitmentSummary

    @property
    def residential_address(self):
        addresses = Addresses(self.address)
        return addresses.residential

    @property
    def work_location(self):
        addresses = Addresses(self.eraddress)
        return addresses.working

    @property
    def selected_contact(self):
        contacts = Contacts(self.contact)
        return contacts.preferredContact

    @property
    def advertisements(self):
        return Advertisements(self.advertisement)

    @property
    def phone_number(self):
        return Phones(self.phone).PreferredPhone

    @property
    def person(self):
        return {
            "full_name": self.personal.full_name,
            "attributive": self.personal.attributive,
            "object": self.personal.object,
            "subject": self.personal.subject,
            "short_name": self.personal.short_name,
            "email": self.personal.email,
            "phone": self.phone_number,
            "address": self.residential_address,
        }

    def context(self, *args, **kwargs):
        context = {
            **self.dict(),
            "advertisement": self.advertisements,
            "personal": self.person,
            "date_of_offer": self.joboffer.date_of_offer,
            "work_start_date": self.joboffer.start_date_say,
            "joboffer_date": self.joboffer.date_of_offer,
            "work_location": self.work_location,
        }
        return context

    def make_pdf_form(self, *args, **kwargs):
        pass

    def make_web_form(self, *args, **kwargs):
        pass
