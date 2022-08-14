"""
.. module:: setup.py

setup.py
******

:Description: setup.py

    Configuration file for apafib python package

:Authors:
    bejar

:Version: 

:Date:  06/05/2022
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="apafib", # Replace with your own username
    version="0.1.0",
    author="Javier Bejar",
    author_email="bejar@cs.upc.edu",
    description="Utilities for GEI APA course",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bejar/apafib",
    packages=['apafib'],
    install_requires=['pandas', 'scikit-learn', 'numpy', 'remotezip'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
