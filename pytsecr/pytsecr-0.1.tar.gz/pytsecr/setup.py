

#!/usr/bin/env python
import os
import sys
from codecs import open

from setuptools import setup
from setuptools.command.test import test as TestCommand

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 7)

if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write(
        """
==========================
Unsupported Python version
==========================
This version of Requests requires at least Python {}.{}, but
you're trying to install it on Python {}.{}. To resolve this,
consider upgrading to a supported Python version.
If you can't upgrade your Python version, you'll need to
pin to an older version of Requests (<2.28).
""".format(
            *(REQUIRED_PYTHON + CURRENT_PYTHON)
        )
    )
    sys.exit(1)
# 'setup.py publish' shortcut.
if sys.argv[-1] == "publish":
    os.system(f"{sys.executable} {sys.argv[0]} sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()
readme = open('README.md', 'r', 'utf-8').read()
setup(name='pytsecr',
      version='0.1',
      
      url='https://pytsecr.readthedocs.io',
      author='pgbito',
      author_email='pgbito@proton.me',
      license='MIT',
  
      package_dir={"pytsecr":"pytsecr"},
      packages=['pytsecr'],
      install_requires=['urllib3', 'html_to_json', 'json', 'requests'],
      description="API Wrapper para interactuar con el sitio web de servicios electorales del Tribunal Supremo de Elecciones, Costa Rica",
      long_description=readme,
      long_description_content_type="text/markdown",
      project_urls={
        "Documentation":'https://pytsecr.readthedocs.io'
        ,'Source': 'https://github.com/pgbito/pytsecr'
      },
      zip_safe=False)
