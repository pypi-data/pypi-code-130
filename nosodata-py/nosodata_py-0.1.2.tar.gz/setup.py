#!/usr/bin/env python3

import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name='nosodata_py',
    version='0.1.2',
    description='Set of classes to read the data from Noso files',
    url='https://github.com/Friends-Of-Noso/NosoData-Py',
    license='MIT',
    author="Gustavo 'Gus' Carreno",
    author_email='guscarreno@gmail.com',
    packages=find_packages(exclude=("tests")),
    long_description=README,
    long_description_content_type="text/markdown"
)
