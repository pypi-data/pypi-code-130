#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

from setuptools import find_packages, find_namespace_packages, setup

# Package meta-data.
NAME = 'M_Shape_Head_Package'
DESCRIPTION = "M Shape Standalone Package for Head"
URL = "https://github.com/NVlabs/SPADE"
EMAIL = "moeharyoso89@gmail.com"
AUTHOR = "Ferdy"
REQUIRES_PYTHON = ">=3.9.0"


# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# Trove Classifiers: https://pypi.org/classifiers/
# If you do change the License, remember to change the
# Trove Classifier for that!
long_description = DESCRIPTION

# Load the package's VERSION file as a dictionary.
about = {}
ROOT_DIR = Path(__file__).resolve().parent
REQUIREMENTS_DIR = ROOT_DIR / 'src/requirements'
PACKAGE_DIR = ROOT_DIR / 'src' 
# with open(PACKAGE_DIR / "VERSION") as f:
#     _version = f.read().strip()
#     # print(_ve)
#     about["__version__"] = _version
# _version = f.read().strip()
# print(_ve)
about["__version__"] = "0.0.5"


# What packages are required for this module to be executed?
def list_reqs(fname="requirements.txt"):
    list = []
    with open(REQUIREMENTS_DIR / fname, 'r', encoding='utf-8') as fd:
        list = fd.read().splitlines()
    return list
################################################ 
print("LIST REQS ASSHOLE: ", list_reqs())
################################################
# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    # SHD BE FINE UNTIL HERE
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    # shd be fine
    # packages=find_packages(exclude=("tests",)),
    # shd be fine
    package_data={"models": ["VERSION"]},
    install_requires=list_reqs(),
    extras_require={},
    include_package_data=True,
    license="BSD-3",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)