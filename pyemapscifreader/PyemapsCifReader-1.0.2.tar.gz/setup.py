# Setup file for creation of the PyCIFRW
# distribution
from __future__ import print_function

from setuptools import setup, Extension, find_packages

#### Do the setup
c_scanner = Extension("emapsCifFile.StarScan",
            sources = ["src/lib/lex.yy.c","src/lib/py_star_scan.c"])

version = {}
with open("__version__.py") as fp:
    exec(fp.read(), version)

setup(name="PyemapsCifReader",
    #   version = "1.0.0",
      version = version['__version__'],
      description = "CIF file reader support for PYEMAPS based on PyCifRead4.4.3",
      author = "EMLab Solutions, Inc.",
      author_email = "support@emlabsoftware.com",
      url="https://www.emlabsolutions.com",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.7',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      py_modules = ['emapsCifFile.CifFile_module','emapsCifFile.yapps3_compiled_rt','emapsCifFile.YappsStarParser_1_1','emapsCifFile.YappsStarParser_1_0',
                    'emapsCifFile.YappsStarParser_STAR2','emapsCifFile.YappsStarParser_2_0','emapsCifFile.StarFile','emapsCifFile.TypeContentsParser'],
      ext_modules = [c_scanner],
      packages = ['emapsCifFile', 'emapsCifFile.drel'],
      test_suite = 'TestPyCIFRW',
      package_dir = {'emapsCifFile':'src'}
      )
