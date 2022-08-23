from typing import List
from model.common.commonmodel import CommonModel, BuilderModel
from model.recruit.jobaddata import JobOffer, General, ErAddress, ErAddresses
from model.common.wordmaker import WordMaker
import os
from model.recruit.jobad import JobadModel, General, JobOffer, ErAddress


class JobadModelE(CommonModel, JobadModel):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/er.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())


class JobadModelDocxAdapater:
    """This is an adapater to bridging job ad model data and docx data"""

    def __init__(self, jobad_obj: JobadModel):
        # get original obj, which will be used to generate some value based on it's object methods.
        # 此处用来处理list里面的一些内容。
        self.jobad_obj = jobad_obj
        addresses = ErAddresses(self.jobad_obj.eraddress)
        self.jobad_obj.eraddress = addresses.working

    def make(self, output_docx, template_no=None):
        template_path = os.path.abspath(os.path.join(DATADIR, "word/jobad.docx"))
        wm = WordMaker(template_path, self.jobad_obj, output_docx)
        wm.make()
