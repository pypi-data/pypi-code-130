from .context import DATADIR
from pydantic import BaseModel
from model.bcpnp.data import General
from model.common.jobposition import PositionBase
from model.common.wordmaker import WordMaker
import os


class Position(PositionBase):
    pass


class CompanyInfoModel(BaseModel):
    general: General
    position: Position


class CompanyInfoDocxAdaptor:
    def __init__(self, employer_training_obj: CompanyInfoModel):
        self.employer_training_obj = employer_training_obj

    def make(self, output_docx):
        template_path = os.path.abspath(
            os.path.join(DATADIR, "word/bcpnp_company_information.docx")
        )
        wm = WordMaker(template_path, self.employer_training_obj, output_docx)
        wm.make()
