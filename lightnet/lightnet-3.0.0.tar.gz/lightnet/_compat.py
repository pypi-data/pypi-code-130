#
#   Lightnet compatibility with older versions (mostly pytorch)
#   Copyright EAVISE
#
from packaging import version
import torch

__all__ = ['meshgrid_kw']
torchversion = version.parse(torch.__version__)


# PyTorch 1.10 : meshgrid takes an extra `indexing` variable
meshgrid_kw = {}
if torchversion >= version.parse('1.10'):
    meshgrid_kw['indexing'] = 'ij'
