#!/usr/bin/env python3

from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='kiddeejoystick',
    packages=['kiddeejoystick'],
    install_requires=['pyserial'],

    version='0.0.1',
    description="A Python Library To Read Data From the Kiddee Joystick - by Kiddee Lab",
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Kiddee Lab',
    author_email='kiddeelab2@gmail.com',
    url='https://github.com/xavjb/kiddeejoystick',
    download_url='https://github.com/xavjb/kiddeejoystick',
    keywords=['Serial Port', 'Arduino', 'Python', 'Kiddee Lab', 'Joystick', 'Gamepad'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)