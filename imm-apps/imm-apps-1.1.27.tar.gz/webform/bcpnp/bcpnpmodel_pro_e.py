from typing import List, Optional
from model.common.address import Address
from model.common.educationbase import EducationBase
from model.common.phone import Phone
from model.common.commonmodel import CommonModel, BuilderModel
from model.common.employmentbase import EmploymentBase
from model.common.jobofferbase import JobofferBase
from model.common.id import ID
from model.common.person import Person
from model.common.language import LanguageBase
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, root_validator, validator
from model.common.utils import normalize
from termcolor import colored
from webform.bcpnp.joboffer_reg import JobofferReg
from webform.bcpnp.login import Login
from webform.bcpnp.registrant import Registrant
from webform.bcpnp.education_reg import EducationReg
from webform.bcpnp.employment import EmploymentReg
from webform.bcpnp.language import LanguageReg
from webform.bcpnp.joboffer_reg import JobofferReg
from webform.bcpnp.submit import Submit
from webform.bcpnp.register import Register
import json

from webform.bcpnp.bcpnpmodel_pro import (
    BcpnpModelPro,
    Personal,
    Address,
    Phone,
    PersonId,
)


class BcpnpModelProE(CommonModel, BcpnpModelPro):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/pa.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
