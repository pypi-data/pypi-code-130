from setuptools import setup
from setuptools.extension import Extension
import numpy as np
import os
import re
from glob import glob
from pathlib import Path


setup(name='GuangBEAT',
      version='1.0',
      description='BEAT',
      author='luzgool',
      author_email='luzgool@berkeley.edu',
      url='https://github.com/luzgool/Casual_Forest',
      packages=['BEAT'],
     )
