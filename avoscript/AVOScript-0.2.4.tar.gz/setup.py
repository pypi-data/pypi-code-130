# -*- coding: utf-8 -*-
from setuptools import find_packages, setup


setup(
    name="AVOScript",
    description="little language just4fun",
    author="Ethosa",
    author_email="social.ethosa@gmail.com",
    version="0.2.4",
    url="https://github.com/ethosa/avoscript",
    install_requires=[
        "colorama",
        "equality",
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
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
