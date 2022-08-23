# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="poinc",
    version="0.1.2",
    author="T.Kato, S.Namba",
    description="Python Open Infrastructure for Network Computing inspired by BOINC project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tetsuji16/poinc",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pysftp >= 0.2"
    ],
)
