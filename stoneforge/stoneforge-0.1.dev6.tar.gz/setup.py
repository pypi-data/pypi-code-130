# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Education",
    "Operating System :: Microsoft :: Windows :: Windows 10",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python ::3"
]

setup(
    name="stoneforge",
    version="0.1.dev6",
    author="GIECAR - UFF",
    url="https://github.com/giecaruff/stoneforge",
    description="Geophysics equations, algorithms and methods",
    long_description=open("README.rst").read(),
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7.13",
    install_requires=[
        "numpy>=1.21.6",
        "pytest>=3.6.4",
        "scipy>=1.4.1",
    ],
)
