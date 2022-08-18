# coding: utf-8

"""
    EBoekhouden API
"""


from setuptools import setup, find_packages  # noqa: H301

NAME = "eboekhoudenapi"
VERSION = "1.2.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "certifi>=2017.4.17",
    "python-dateutil>=2.1",
    "six>=1.10",
    "urllib3>=1.23"
]
    

setup(
    name=NAME,
    version=VERSION,
    description="EBoekhouden API",
    author_email="",
    url="",
    keywords=["Soap", "EBoekhouden API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description=""
)