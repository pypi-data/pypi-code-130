#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

from setuptools import find_packages, setup

# Package meta-data.
NAME = 'mlmodelswrapper'
DESCRIPTION = "Python ML Models"
URL = "https://github.com/lp-dataninja/learning_packaging"
EMAIL = "lp.dataninja@gmai.com"
AUTHOR = "Ladle Patel"
REQUIRES_PYTHON = ">=3.6.0"


# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the
# Trove Classifier for that!
long_description = DESCRIPTION

# Load the package's VERSION file as a dictionary.
about = {}
ROOT_DIR = Path(__file__).resolve().parent
REQUIREMENTS_DIR = ROOT_DIR / 'requirements'



# What packages are required for this module to be executed?
def list_reqs(fname="requirements.txt"):
    with open(REQUIREMENTS_DIR / fname) as fd:
        return fd.read().splitlines()

# Where the magic happens:
setup(
    name='mlmodelswrapper',
    version='0.0.4',
    description=DESCRIPTION,
    long_description=long_description,
    author="Ladle Patel",
    author_email="lp.dataninja@gmail.com",
    python_requires=REQUIRES_PYTHON,
    py_modules=["helloladle"],
    package_dir={'': 'src'},
    url=URL,
    install_requires=list_reqs(),
    extras_require={},
    license="BSD-3",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)