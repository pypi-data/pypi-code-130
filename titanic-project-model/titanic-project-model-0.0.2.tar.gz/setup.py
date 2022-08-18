#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages

# Where the magic happens:
setup(
    name='titanic-project-model',
    version='0.0.2',
    description="Example regression model package from Train In Data.",
    author='Liliya Kazykhanova',
    author_email='kazychanowa.liliya@gmail.com',
    python_requires=">=3.8.0",
    url='https://github.com/LiliyaKazykhanova/titanic-project',
    packages=find_packages(exclude=("tests",)),
)
