# -*- coding: utf-8 -*-

import os
import sys

if 'bdist_wheel' in sys.argv:
    # to build wheel, use 'python setup.py sdist bdist_wheel'
    from setuptools import setup 
else:
    from distutils.core import setup # 'python setup.py install'
    

__title__ = 'utils_hoo'
here = os.path.abspath(os.path.dirname(__file__))
pkg_info = {}
fpath= os.path.join(here, __title__, '_pkg_info.py')
with open(fpath, 'r') as f:
    exec(''.join(f.readlines()))


setup(name=__title__,
      version=pkg_info['__version__'],
      author=pkg_info['__author__'],
      author_email=pkg_info['__author_email__'],
      url=pkg_info['__url__'],
      license=pkg_info['__license__'],
      description=pkg_info['__description__'],
      long_description=pkg_info['__long_description__'],
      platforms='any',
      packages=['utils_hoo',
                'utils_hoo.utils_logging',
                'utils_hoo.utils_plot',
                'utils_hoo.utils_datsci',
                'utils_hoo.utils_datsci.AHP',
                'utils_hoo.utils_datsci.ELM',
                'utils_hoo.utils_fin',
				'utils_hoo.utils_sql',
				'utils_hoo.utils_optimizer',
				'utils_hoo.utils_html',
                'utils_hoo.BackPacks',
                'utils_hoo.FindAddends',
                'utils_hoo.Sorts',
                'utils_hoo.utils_other',
                'utils_hoo.tmp'])


