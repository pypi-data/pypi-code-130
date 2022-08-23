from .context import DATADIR
from model.common.commonmodel import CommonModel
from model.bcpnp.data import JobOffer
from model.common.person import Person
from model.common.wordmaker import WordMaker
import os
from model.bcpnp.jobdescription import JobDescriptionModel, Personal


class JobDescriptionModelE(CommonModel, JobDescriptionModel):
    personal: Personal
    joboffer: JobOffer
    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/er.xlsx", "excel/pa.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
