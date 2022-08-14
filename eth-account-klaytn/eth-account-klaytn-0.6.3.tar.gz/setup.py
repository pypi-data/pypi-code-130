#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    setup,
    find_packages,
)

extras_require = {
    'test': [
        "hypothesis>=4.18.0,<5",
        "pytest>=6.2.5,<7",
        "pytest-xdist",
        "tox==3.25.0",
    ],
    'lint': [
        "flake8==3.7.9",
        "isort>=4.2.15,<5",
        "mypy==0.910",
        "pydocstyle>=5.0.0,<6",
    ],
    'doc': [
        "Sphinx>=1.6.5,<5",
        "jinja2>=3.0.0,<3.1.0",  # jinja2<3.0 or >=3.1.0 cause doc build failures.
        "sphinx_rtd_theme>=0.1.9,<1",
        "towncrier==18.5.0",  # towncrier doesn't follow semver
    ],
    'dev': [
        "bumpversion>=0.5.3,<1",
        "pytest-watch>=4.1.0,<5",
        "wheel",
        "twine",
        "ipython",
    ],
}

extras_require['dev'] = (
    extras_require['dev'] +  # noqa: W504
    extras_require['test'] +  # noqa: W504
    extras_require['lint'] +  # noqa: W504
    extras_require['doc']
)


with open('./README.md', encoding='utf-8') as readme:
    long_description = readme.read()


setup(
    name='eth-account-klaytn',
    # *IMPORTANT*: Don't manually change the version here. Use `make bump`, as described in readme
    version='0.6.3',
    description="""eth-account-klaytn: Sign Ethereum transactions and messages with local private keys + klaytn""",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Daniel Bae',
    author_email='daniel.bae@devcra.com',
    url='https://github.com/DevCra/eth-account-klaytn',
    include_package_data=True,
    package_data={"eth_account_klaytn": [
        "py.typed",
        "hdaccount/wordlist/*.txt",
    ]},
    install_requires=[
        "bitarray>=2.4.0,<3",
        "eth-abi>=3.0.0,<4",
        "eth-keyfile>=0.6.0,<0.7.0",
        "eth-keys>=0.4.0,<0.5",
        "eth-rlp>=0.3.0,<1",
        "eth-utils>=2.0.0,<3",
        "hexbytes>=0.1.0,<1",
        "rlp>=1.0.0,<4"
    ],
    python_requires='>=3.6, <4',
    extras_require=extras_require,
    py_modules=['eth_account_klaytn'],
    license="MIT",
    zip_safe=False,
    keywords='ethereum',
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
