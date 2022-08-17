#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
from distutils.util import convert_path

main_ns = {}
ver_path = convert_path('sentency/_version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['spacy']

test_requirements = ['pytest>=3', ]

setup(
    author="Grant DeLong",
    author_email='gdelong1@geisinger.edu',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A small lspaCy pipeline component for matching within document sentences using regular expressi",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='sentency',
    name='sentency',
    packages=find_packages(include=['sentency', 'sentency.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/g-delong/sentency',
    version=main_ns["__version__"],
    zip_safe=False,
)
