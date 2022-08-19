"""
Models (:mod:`saullo_castro_tenure_review.models`)
==================================================

.. currentmodule:: saullo_castro_tenure_review.models

"""
from .modelpyfe3d import ModelPyFE3D
from .data.pCRM9_wing import PATH_TO_PCRM9_WING
from .dataset import zenodo_urls, files_from_urls


class pCRM9_wing(object):
    def __init__(self, from_doi=False):
        self.doi = 'https://doi.org/10.5281/zenodo.6390714'
        self.from_doi = from_doi
        if from_doi:
            path = ''
        else:
            path = PATH_TO_PCRM9_WING + '/'
        self.file_names = [
                path + 'pCRM9_103_MAIN_FILE.bdf', # NOTE main file
                path + 'pCRM9_CONM2_MTOW.dat',
                path + 'pCRM9_mat.dat',
                path + 'pCRM9_model_2.dat',
                path + 'pCRM9_PSHELL.dat',
                path + 'pCRM9_ribs_fem.dat',
                ]
        if from_doi:
            urls = zenodo_urls(self.doi, self.file_names)
            files_from_urls(urls)

    def pyfe3d_model(self):
        model = ModelPyFE3D()
        model.read_nastran(self.file_names[0])

        return model

