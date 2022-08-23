#!/usr/bin/env python

from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='pyKamipi',
    packages=['pyKamipi'],
    install_requires=['pyserial'],

    version='0.9',
    description="A Python Library For Kamibot-Pi",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='devdio',
    author_email='kei.devdio@gmail.com',
    url='https://github.com/devdio/pyKamipi.git',
    keywords=['Kamibot Pi', 'KamibotPi', 'Robot'],
    python_requires='>=3.7',
    classifiers=[
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
