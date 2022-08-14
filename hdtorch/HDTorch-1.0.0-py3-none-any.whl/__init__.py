__version__ = '1.0.0'
__name__ = 'hdtorch'

#from distutils.core import setup, Extension
#from torch.utils.cpp_extension import BuildExtension, CUDAExtension

#module1 = CUDAExtension('hdtorch', sources = ['cuda/hdtorch.cpp', 'cuda/hdtorch_cu.cu'],
#                        extra_compile_args=["-O3"])

#setup(name='hdtorch',
#      ext_modules=[module1],
#      cmdclass={'build_ext': BuildExtension})

import os
from pathlib import Path
from torch.utils.cpp_extension import load
_hdtorchcuda = load(
    name='hdtorchcuda',
    extra_cflags=['-O3'],
    is_python_module=True,
    sources=[
        os.path.join(Path(__file__).parent, 'cuda', 'hdtorch.cpp'),
        os.path.join(Path(__file__).parent, 'cuda', 'hdtorch_cu.cu')
    ]
)



#from .cuda import setup
from . import util
from .model import HD_classifier
