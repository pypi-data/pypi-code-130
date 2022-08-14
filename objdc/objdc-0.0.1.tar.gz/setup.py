#!/usr/bin/env python

from distutils.core import setup

setup(name='objdc',
  version='0.0.1',
  description='Object Data Converter',
  author='Mikhail Efremov',
  author_email='meechanic.design@gmail.com',
  url='https://github.com/meechanic/',
  license="MIT",
  scripts=['bin/objdc'],
  packages=['objdc']
)
