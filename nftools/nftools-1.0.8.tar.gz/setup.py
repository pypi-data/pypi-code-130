#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
from nftools import __version__

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['click~=8.1.3',
                'aiohttp~=3.8.1',
                'base58~=2.1.1',
                'pandas~=1.3.5',
                'requests~=2.28.1',
                'setuptools~=60.2.0',
                'tqdm==4.64.0']

test_requirements = []

setup(
    author="Jim Eagle",
    author_email='akajimeagle@pm.me',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="A CLI for managing your solana nft collection.",
    entry_points={
        'console_scripts': [
            'nftools=nftools.__main__:main'
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='nftools',
    name='nftools',
    packages=find_packages(include=['nftools', 'nftools.*']),
    test_suite='tests',
    setup_requires=['tqdm>=4.0.0'],
    tests_require=test_requirements,
    url='https://github.com/akajimeagle/nftools',
    version=__version__,
    zip_safe=False,
)

print(find_packages(include=['nftools', 'nftools.*']))
