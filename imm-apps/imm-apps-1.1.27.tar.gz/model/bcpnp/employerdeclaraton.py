from typing import List
from model.common.commonmodel import CommonModel, BuilderModel
from model.bcpnp.data import Bcpnp, Contact, General, JobOffer, ErAddress
from model.common.jobposition import PositionBase
from model.common.rcic import Rcic
from model.common.advertisement import (
    Advertisement,
    Advertisements,
    InterviewRecord,
    InterviewRecords,
    RecruitmentSummary,
)
from model.common.person import Person, PersonalAssess
from model.common.contact import Contacts
from model.common.address import Addresses
from model.common.phone import Phone, Phones
from datetime import date
from model.common.xmlfiller import XmlFiller
import os
from typing import Optional
from pdfform.bcpnp.fbemployerdeclaration import FormBuilderEmployerDeclaration
from pydantic import BaseModel


class Personal(Person):
    def __str__(self):
        return self.full_name


class Position(PositionBase):
    is_new: bool
    has_same_number: Optional[int]
    vacancies_number: Optional[int]
    laidoff_with12: Optional[int]
    laidoff_current: Optional[int]


class EmployerDeclaratonFormModel(BaseModel, BuilderModel):
    eraddress: List[ErAddress]
    phone: List[Phone]
    general: General
    contact: List[Contact]
    position: Position
    personal: Personal
    joboffer: JobOffer
    personalassess: PersonalAssess
    # bcpnp: Bcpnp
    rcic: Rcic
    advertisement: List[Advertisement]
    interviewrecord: List[InterviewRecord]
    recruitmentsummary: RecruitmentSummary

    @property
    def work_location(self):
        addresses = Addresses(self.eraddress)
        return addresses.working

    @property
    def phones(self):
        return Phones(self.phone)

    @property
    def selected_contact(self):
        contacts = Contacts(self.contact)
        return contacts.preferredContact

    @property
    def interviews(self):
        return InterviewRecords(self.interviewrecord)

    @property
    def advertisements(self):
        return Advertisements(self.advertisement)

    @property
    def businessaddress(self):
        eraddress = Addresses(self.eraddress)
        return eraddress.business

    @property
    def mailingaddress(self):
        eraddress = Addresses(self.eraddress)
        return eraddress.mailing

    @property
    def person(self):
        return {
            "first_name": self.personal.first_name,
            "last_name": self.personal.last_name,
            "full_name": self.personal.full_name,
            "attributive": self.personal.attributive,
            "object": self.personal.object,
            "subject": self.personal.subject,
            "short_name": self.personal.short_name,
            "why_tfw": self.personalassess.why_qualified_say,
        }

    def context(self, *args, **kwargs):
        pass

    def make_pdf_form(self, output_json, *args, **kwargs):
        pf = FormBuilderEmployerDeclaration(self)
        pf.save(output_json)

    def make_web_form(self, *args, **kwargs):
        pass
