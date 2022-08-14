#!/usr/bin/env python3

from setuptools import setup
from setuptools import find_namespace_packages

setup(
    name="pybrotherqlprinter",
    version="1.0",
    packages=find_namespace_packages(
        where=".",
    ),
    install_requires=[
        'Pillow',
    ],
)
