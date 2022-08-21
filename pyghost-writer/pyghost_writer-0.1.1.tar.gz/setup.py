#!/usr/bin/env python
# -*- coding: utf-8 -*-


import versioneer
from setuptools import setup


setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    entry_points={
        'console_scripts': [
            'scriptify_py = ghost_writer.scripts.cmd_line:scriptify_py',
        ]
    },
)
