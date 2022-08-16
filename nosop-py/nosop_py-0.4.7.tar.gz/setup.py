#!/usr/bin/env python3

import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name='nosop_py',
    version='0.4.7',
    description='Set of classes and tools to communicate with a Noso wallet using NosoP',
    url='https://github.com/Friends-Of-Noso/NosoP-Py',
    license='MIT',
    author="Gustavo 'Gus' Carreno",
    author_email='guscarreno@gmail.com',
    packages=find_packages(exclude=("tests")),
    long_description=README,
    long_description_content_type="text/markdown"
)
