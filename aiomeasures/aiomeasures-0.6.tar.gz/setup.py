#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='aiomeasures',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version="0.6",
    description="Squatted pypi package",
    author="Xavier Barbosa",
    author_email='clint.northwood@gmail.com',
    url='http://lab.errorist.xyz/abc/',
    packages=find_packages(),
    keywords=[''],
    install_requires=[],
    classifiers=[
        "Development Status :: 7 - Inactive"
    ]
)