#!/usr/bin/env python

from io import open
from setuptools import setup

"""
:authors: two-it2022
:license: Apache License, Version 0.1, see LICENSE file
:copyright: (c) 2022 two-it2022
"""

version = '0.0.1'
'''
with open('__readme__.md', encoding='utf-8') as f:
      long_description = f.read()
'''

long_description = '''Python module for Two It project
                  management platform (TwoIt API wrapper)'''


setup(
      name='mcoms',
      version=version,

      author='two-it2022',
      author_email='kodland.group@gmail.com',

      description=(
            u'Installing'
            u'''
Open the CMD. And enter: pip install mcoms or pip install mcoms==[nevest_version]
Create the file [your_file_name].py and write in file: import mcoms or from speaker import *
            '''
      ),
      long_description=long_description,
      #long_description_content_type='text/markdown',

      url='https://github.com/TwoIt202/mcoms',
      download_url='https://github.com/TwoIt202/mcoms/raw/7a9c3e5770a548e1beb6381c8df18db0c5015a34/mcoms.zip'.format(
            version
      ),

      license='Apache License, Version 0.1, see LICENSE file',

      packages=['mcoms'],
      install_requires=['flask', 'translate', 'colorama', 'termcolor'],

      classifiers=[
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Programming Language :: Python :: Implementation :: CPython',
      ]

)