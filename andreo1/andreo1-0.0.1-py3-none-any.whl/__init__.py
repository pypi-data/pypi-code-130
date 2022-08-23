"""
See the readme at https://pypi.org/project/andreo/
or do the follow code:

import andreo

andreo.help()
"""
from .__return__ import img
from .__par__ import PdfCutReader, recortaUmaPagina, help_Me

__all__ = ['help()',
           'leUmaPaginaInteira(pdfPath: str, pagina: int)',
           'recortaUmaPagina']