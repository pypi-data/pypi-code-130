import os
import sys
from pathlib import Path

from setuptools import find_packages, setup
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(name='payok',
      version='1.1',
      description="Python payok.io API Client",
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=['payok'],
      author='except',
      author_email='994b3d@gmail.com',
      url='https://github.com/re-oos/payok',
      license='MIT LICENSE',
      zip_safe=False,
    install_requires=[
        'requests',
    ]
      )
