import setuptools
from distutils.core import setup

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='tg_log_handler',
      version='0.0.1',
      description='Async Telegram Logging Handler',
      long_description=long_description,
      url='https://lolz.guru/members/2977610/',
      author='zcxw',
      packages=setuptools.find_packages(),
      install_requires=['requests~=2.27.0', 'retry~=0.9.0']
      )
