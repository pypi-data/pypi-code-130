from .context import DATADIR
from typing import List
from model.common.commonmodel import CommonModel, BuilderModel
from model.recruit.jobofferdata import JobOffer, General, ErAddress, ErAddresses
from model.common.address import Address, Addresses
from model.common.person import Person
from model.common.wordmaker import WordMaker
import os
from model.recruit.joboffer import (
    JobofferModel,
    General,
    JobOffer,
    ErAddress,
    Address,
    Personal,
)


class JobofferModelE(CommonModel, JobofferModel):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/pa.xlsx", "excel/er.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())


class JobofferModelDocxAdapater:
    """This is an adapater to bridging job ad model data and docx data"""

    def __init__(self, joboffer_obj: JobofferModel):
        # get original obj, which will be used to generate some value based on it's object methods.
        # 此处用来处理list里面的一些内容。
        self.joboffer_obj = joboffer_obj
        eraddresses = ErAddresses(self.joboffer_obj.eraddress)
        self.joboffer_obj.eraddress = eraddresses.working

        addresses = Addresses(self.joboffer_obj.address)
        self.joboffer_obj.address = addresses.residential

    def make(self, output_docx, template_no=None):
        file_name = "word/joboffer" + str(template_no) + ".docx"
        template_path = os.path.abspath(os.path.join(DATADIR, file_name))
        wm = WordMaker(template_path, self.joboffer_obj, output_docx)
        wm.make()
