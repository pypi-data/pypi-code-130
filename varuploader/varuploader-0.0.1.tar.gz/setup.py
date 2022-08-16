# Copyright 2022 Variscite LTD - Recovery SD Card Uploader Tool
# SPDX-License-Identifier: BSD-3-Clause

import os
from setuptools import setup, find_packages

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = "varuploader",
    version = "0.0.1",
    author = "Alifer Moraes, Diego Dorta",
    description = "Variscite Recovery SD Card Uploader Tool",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license = "BSD-3-Clause",
    url = "https://github.com/dorta/var-uploader",
    packages=find_packages(),
    entry_points = {
        'console_scripts' : ['varuploader = varuploader.varuploader:main']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'Natural Language :: English',
        'Operating System :: Other OS',
        'Programming Language :: Python :: 3.7'
    ],
)
