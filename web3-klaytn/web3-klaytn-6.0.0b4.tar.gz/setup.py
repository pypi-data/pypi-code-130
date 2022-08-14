#!/usr/bin/env python
from setuptools import (
    find_packages,
    setup,
)

extras_require = {
    'tester': [
        "eth-tester[py-evm]==v0.6.0-beta.5",
        "py-geth>=3.8.0,<4",
    ],
    'linter': [
        "black>=22.1.0,<23.0",
        "flake8==3.8.3",
        "isort>=4.2.15,<4.3.5",
        "mypy==0.910",
        "types-setuptools>=57.4.4,<58",
        "types-requests>=2.26.1,<3",
        "types-protobuf==3.19.13",
    ],
    'docs': [
        "mock",
        "sphinx-better-theme>=0.1.4",
        "click>=5.1",
        "configparser==3.5.0",
        "contextlib2>=0.5.4",
        "py-geth>=3.8.0,<4",
        "py-solc>=0.4.0",
        "pytest>=6.2.5,<7",
        "sphinx>=4.2.0,<5",
        "sphinx_rtd_theme>=0.1.9",
        "toposort>=1.4",
        "towncrier==18.5.0",
        "urllib3",
        "wheel"
    ],
    'dev': [
        "bumpversion",
        "flaky>=3.7.0,<4",
        "hypothesis>=3.31.2,<6",
        "pytest>=6.2.5,<7",
        "pytest-asyncio>=0.18.1,<0.19",
        "pytest-mock>=1.10,<2",
        "pytest-pythonpath>=0.3",
        "pytest-watch>=4.2,<5",
        "pytest-xdist>=1.29,<2",
        "setuptools>=38.6.0",
        "tox>=1.8.0",
        "tqdm>4.32,<5",
        "twine>=1.13,<2",
        "pluggy==0.13.1",
        "when-changed>=0.3.0,<0.4"
    ]
}

extras_require['dev'] = (
    extras_require['tester']
    + extras_require['linter']
    + extras_require['docs']
    + extras_require['dev']
)

with open('./README.md', encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='web3-klaytn',
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    version='6.0.0-beta.4',
    description="""Web3.py-klaytn""",
    long_description_content_type='text/markdown',
    long_description=long_description,
    author='Daniel Bae',
    author_email='daniel.bae@devcra.com',
    url='https://github.com/DevCra/web3.py-klaytn',
    include_package_data=True,
    install_requires=[
        "aiohttp>=3.7.4.post0,<4",
        "eth-abi>=3.0.0,<4.0.0",
        "eth-account-klaytn>=0.6.0,<0.7.0",
        "eth-hash[pycryptodome]>=0.2.0,<1.0.0",
        "eth-typing>=3.0.0,<4.0.0",
        "eth-utils>=2.0.0,<3.0.0",
        "hexbytes>=0.1.0,<1.0.0",
        "ipfshttpclient==0.8.0a2",
        "jsonschema>=4.0.0,<5",
        "lru-dict>=1.1.6,<2.0.0",
        "protobuf>=3.10.0,<4",
        "pywin32>=223;platform_system=='Windows'",
        "requests>=2.16.0,<3.0.0",
        # remove typing_extensions after python_requires>=3.8, see web3._utils.compat
        "typing-extensions>=3.7.4.1,<5;python_version<'3.8'",
        "websockets>=10.0.0,<11",
    ],
    python_requires='>=3.7.2,<3.11',
    extras_require=extras_require,
    py_modules=['web3', 'ens', 'ethpm'],
    entry_points={"pytest11": ["pytest_ethereum = web3.tools.pytest_ethereum.plugins"]},
    license="MIT",
    zip_safe=False,
    keywords='ethereum',
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"web3": ["py.typed"]},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
