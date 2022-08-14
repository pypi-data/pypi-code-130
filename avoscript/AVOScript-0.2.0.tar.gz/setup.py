# -*- coding: utf-8 -*-
from distutils.core import setup

import setuptools

with open('readme.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="AVOScript",
    description="little language just4fun",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ethosa",
    author_email="social.ethosa@gmail.com",
    version="0.2.0",
    url="https://github.com/ethosa/avoscript",
    install_requires=[
        "colorama",
        "equality",
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.10',
    keywords=['language', 'avocat', 'avoscript', 'script language'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development',
    ]
)
