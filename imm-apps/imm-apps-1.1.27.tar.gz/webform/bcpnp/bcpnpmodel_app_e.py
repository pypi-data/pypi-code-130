from typing import List, Optional
from model.common.address import Address
from model.common.educationbase import EducationBase
from model.common.commonmodel import CommonModel
from model.common.employmentbase import EmploymentBase
from model.common.jobofferbase import JobofferBase
from model.common.id import ID
from model.common.person import Person
from model.common.cor import CORs, COR
from model.common.status import Status
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, root_validator, validator
from model.common.utils import normalize
from webform.bcpnp.submit import Submit
from webform.bcpnp.family import FamilyApp
from model.common.contact import ContactBase
from model.common.family import FamilyBase
from termcolor import colored
from webform.bcpnp.applicant import Applicant
from webform.bcpnp.education_app import EducationApp
from webform.bcpnp.workexperience import WorkExperience
from webform.bcpnp.joboffer_app import JobofferApp
from webform.bcpnp.submit import Submit
from webform.bcpnp.login import Login
import json
from webform.bcpnp.bcpnpmodel_app import (
    BcpnpModelApp,
    BcpnpEEModelApp,
    Personal,
    Marriage,
    COR,
    General,
    Joboffer,
    Family,
    ErAddress,
    Contact,
    Bcpnp,
    Education,
    Employment,
    CanadaRelative,
    Rcic,
    Ee,
)


class BcpnpModelAppE(CommonModel, BcpnpModelApp):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = [
            "excel/er.xlsx",
            "excel/pa.xlsx",
            "excel/bcpnp.xlsx",
            "excel/rep.xlsx",
        ]
        super().__init__(excels, output_excel_file, mother_excels, globals())


class BcpnpEEModelAppE(CommonModel, BcpnpEEModelApp):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = [
            "excel/er.xlsx",
            "excel/pa.xlsx",
            "excel/bcpnp.xlsx",
            "excel/rep.xlsx",
        ]
        super().__init__(excels, output_excel_file, mother_excels, globals())
