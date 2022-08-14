# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

__version__ = "0.1.0"

setup(
    name="pathman2",
    version=__version__,
    author="Zach Duey",
    author_email="zachduey@gmail.com",
    description=(
        "Pathlib-style interface for local, remote, and cloud-based file systems"
    ),
    packages=find_packages(exclude=["tests"]),
    package_dir={"pathman2": "pathman2"},
    package_data={"pathman2": ["py.typed"]},
    install_requires=[],
    extras_require={
        "s3": ["s3fs"]
    },
    license="MIT",
    classifiers=["Development Status :: 3 - Alpha", "Topic :: Utilities"],
)
