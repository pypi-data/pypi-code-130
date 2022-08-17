from setuptools import setup, find_packages

from codecs import open
from os import path

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="tidal_unofficial",
    version="0.0.2",
    description="An unofficial library to use Tidal's API where the authorization is not required",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bocchilorenzo/tidal_unofficial",
    author="Lorenzo Bocchi",
    author_email="lorenzobocchi99@yahoo.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=["tidal_unofficial"],
    include_package_data=True,
    install_requires=["requests"]
)
