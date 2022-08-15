# -*- coding: utf-8 -*-
"""A static blog generator
"""

from __future__ import print_function

import os
from setuptools import setup

import baicaoyuan


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='baicaoyuan',
    version=baicaoyuan.version,
    license='AGPL 3.0',
    url = "https://bcy.hello8693.xyz/",
    description='A community version of baicaoyuan',
    long_description=read('README.md'),
    keywords = "dsz baicaoyuan bcy dianshizhu tvzhu",

    author='hello8693',
    author_email='hello8693@hello8693.xyz',

    packages=['baicaoyuan'],
    include_package_data = True,
    package_data={
        'baicaoyuan': [
            'config.yml',
            'themes/default/*.html',
            'themes/default/*.xml',
            'themes/default/assets/css/*.css',
            'themes/default/assets/js/*.js',
            'themes/default/assets/img/*.*',
            'themes/default/assets/other/*.*',

        ],
    },

    python_requires='>=3',

    classifiers=[
        "Programming Language :: Python :: 3",
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        
        'Intended Audience :: Developers',
        
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Topic :: Utilities',
    ],

    install_requires=['Jinja2', 'Markdown', 'Pygments', 'PyYAML', 'docopt', 'requests'],

    py_modules=['baicaoyuan'],

    entry_points={
        'console_scripts': [
            'baicaoyuan=baicaoyuan.cmd:main',
        ],
    },

    test_suite = 'test',
)
