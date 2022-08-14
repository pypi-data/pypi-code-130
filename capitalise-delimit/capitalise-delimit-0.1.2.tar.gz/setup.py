from setuptools import setup

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="capitalise-delimit",
    version="0.1.2",
    description="Capitalise string by delimiters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jkoninger/capitalise-delimit",
    author="Jahan Köninger",
    author_email="jck999992@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=["capitalise_delimit"],
    include_package_data=True,
    install_requires=[]
)
