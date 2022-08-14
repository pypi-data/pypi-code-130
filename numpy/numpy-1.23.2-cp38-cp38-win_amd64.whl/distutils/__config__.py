# This file is generated by numpy's setup.py
# It contains system_info results at the time of building this package.
__all__ = ["get_info","show"]


import os
import sys

extra_dll_dir = os.path.join(os.path.dirname(__file__), '.libs')

if sys.platform == 'win32' and os.path.isdir(extra_dll_dir):
    os.add_dll_directory(extra_dll_dir)

openblas64__info={'library_dirs': ['D:\\a\\numpy\\numpy\\build\\openblas64__info'], 'libraries': ['openblas64__info'], 'language': 'f77', 'define_macros': [('HAVE_CBLAS', None), ('BLAS_SYMBOL_SUFFIX', '64_'), ('HAVE_BLAS_ILP64', None)]}
blas_ilp64_opt_info={'library_dirs': ['D:\\a\\numpy\\numpy\\build\\openblas64__info'], 'libraries': ['openblas64__info'], 'language': 'f77', 'define_macros': [('HAVE_CBLAS', None), ('BLAS_SYMBOL_SUFFIX', '64_'), ('HAVE_BLAS_ILP64', None)]}
openblas64__lapack_info={'library_dirs': ['D:\\a\\numpy\\numpy\\build\\openblas64__lapack_info'], 'libraries': ['openblas64__lapack_info'], 'language': 'f77', 'define_macros': [('HAVE_CBLAS', None), ('BLAS_SYMBOL_SUFFIX', '64_'), ('HAVE_BLAS_ILP64', None), ('HAVE_LAPACKE', None)]}
lapack_ilp64_opt_info={'library_dirs': ['D:\\a\\numpy\\numpy\\build\\openblas64__lapack_info'], 'libraries': ['openblas64__lapack_info'], 'language': 'f77', 'define_macros': [('HAVE_CBLAS', None), ('BLAS_SYMBOL_SUFFIX', '64_'), ('HAVE_BLAS_ILP64', None), ('HAVE_LAPACKE', None)]}

def get_info(name):
    g = globals()
    return g.get(name, g.get(name + "_info", {}))

def show():
    """
    Show libraries in the system on which NumPy was built.

    Print information about various resources (libraries, library
    directories, include directories, etc.) in the system on which
    NumPy was built.

    See Also
    --------
    get_include : Returns the directory containing NumPy C
                  header files.

    Notes
    -----
    1. Classes specifying the information to be printed are defined
       in the `numpy.distutils.system_info` module.

       Information may include:

       * ``language``: language used to write the libraries (mostly
         C or f77)
       * ``libraries``: names of libraries found in the system
       * ``library_dirs``: directories containing the libraries
       * ``include_dirs``: directories containing library header files
       * ``src_dirs``: directories containing library source files
       * ``define_macros``: preprocessor macros used by
         ``distutils.setup``
       * ``baseline``: minimum CPU features required
       * ``found``: dispatched features supported in the system
       * ``not found``: dispatched features that are not supported
         in the system

    2. NumPy BLAS/LAPACK Installation Notes

       Installing a numpy wheel (``pip install numpy`` or force it
       via ``pip install numpy --only-binary :numpy: numpy``) includes
       an OpenBLAS implementation of the BLAS and LAPACK linear algebra
       APIs. In this case, ``library_dirs`` reports the original build
       time configuration as compiled with gcc/gfortran; at run time
       the OpenBLAS library is in
       ``site-packages/numpy.libs/`` (linux), or
       ``site-packages/numpy/.dylibs/`` (macOS), or
       ``site-packages/numpy/.libs/`` (windows).

       Installing numpy from source
       (``pip install numpy --no-binary numpy``) searches for BLAS and
       LAPACK dynamic link libraries at build time as influenced by
       environment variables NPY_BLAS_LIBS, NPY_CBLAS_LIBS, and
       NPY_LAPACK_LIBS; or NPY_BLAS_ORDER and NPY_LAPACK_ORDER;
       or the optional file ``~/.numpy-site.cfg``.
       NumPy remembers those locations and expects to load the same
       libraries at run-time.
       In NumPy 1.21+ on macOS, 'accelerate' (Apple's Accelerate BLAS
       library) is in the default build-time search order after
       'openblas'.

    Examples
    --------
    >>> import numpy as np
    >>> np.show_config()
    blas_opt_info:
        language = c
        define_macros = [('HAVE_CBLAS', None)]
        libraries = ['openblas', 'openblas']
        library_dirs = ['/usr/local/lib']
    """
    from numpy.core._multiarray_umath import (
        __cpu_features__, __cpu_baseline__, __cpu_dispatch__
    )
    for name,info_dict in globals().items():
        if name[0] == "_" or type(info_dict) is not type({}): continue
        print(name + ":")
        if not info_dict:
            print("  NOT AVAILABLE")
        for k,v in info_dict.items():
            v = str(v)
            if k == "sources" and len(v) > 200:
                v = v[:60] + " ...\n... " + v[-60:]
            print("    %s = %s" % (k,v))

    features_found, features_not_found = [], []
    for feature in __cpu_dispatch__:
        if __cpu_features__[feature]:
            features_found.append(feature)
        else:
            features_not_found.append(feature)

    print("Supported SIMD extensions in this NumPy install:")
    print("    baseline = %s" % (','.join(__cpu_baseline__)))
    print("    found = %s" % (','.join(features_found)))
    print("    not found = %s" % (','.join(features_not_found)))

