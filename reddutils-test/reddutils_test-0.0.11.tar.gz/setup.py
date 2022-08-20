#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

path1 = 'exodus/data/tables'

setuptools.setup(
    name="reddutils_test",
    version="0.0.11",
    author="ReddTea",
    author_email="redd@tea.com",
    description="Small package for personal use",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="https://github.com/pypa/sampleproject",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    #data_files=[(path1, [path1+'/exo_list.csv', path1+'/ss_list.csv'])],
    include_package_data=True,
    install_requires=['numpy'],
    python_requires=">=3.6",
)
