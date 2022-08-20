#!/usr/bin/env python3

from setuptools import setup
from vkostyanetsky.cliutils.version import __version__


setup(
    name="vkostyanetsky.cliutils",
    version=__version__,
    description="A tiny library that makes CLI apps development a bit faster.",
    long_description=open("README.md", encoding="utf-8-sig").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vkostyanetsky/CLIUtils",
    license="MIT",
    python_requires=">=3.7",
    packages=["vkostyanetsky.cliutils"],
    install_requires=[],
    author="Vlad Kostyanetsky",
    author_email="vlad@kostyanetsky.me",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="cli console menu progressbar",
)
