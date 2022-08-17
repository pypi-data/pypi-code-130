from setuptools import setup, find_packages
import os

VERSION = '0.0.6'
DESCRIPTION = 'Package to make nlp model off twitter user data'
LONG_DESCRIPTION = 'Package to make nlp model off twitter user data with Markov Chains'

# Setting up
setup(
    name="little_t",
    version=VERSION,
    author="Alex McCune",
    author_email="alexmccune1224@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
