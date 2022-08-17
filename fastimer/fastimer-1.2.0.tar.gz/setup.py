#!/usr/bin/env python3

from setuptools import setup
from fastimer.version import __version__


setup(
    name="fastimer",
    version=__version__,
    description="A simple CLI tool to track food you consume",
    long_description=open("README.md", encoding="utf-8-sig").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vkostyanetsky/Fastimer",
    license="MIT",
    python_requires=">=3.7",
    packages=["fastimer"],
    install_requires=[
        "PyYAML~=6.0",
        "keyboard~=0.13.5",
        "vkostyanetsky.cliutils~=0.1.0",
    ],
    entry_points={"console_scripts": ["fastimer=fastimer.fastimer:main"]},
    author="Vlad Kostyanetsky",
    author_email="vlad@kostyanetsky.me",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
    keywords="fasting fast",
)
