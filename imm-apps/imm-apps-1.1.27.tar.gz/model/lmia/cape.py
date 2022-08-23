from model.common.commonmodel import CommonModel
from model.lmia.cap import CapModel, CapTFW, General, LmiaCase


class CapModelE(CommonModel, CapModel):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/er.xlsx", "excel/lmia.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
