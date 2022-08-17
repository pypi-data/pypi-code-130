# coding=utf-8
# *** WARNING: generated file
from setuptools import setup, find_packages


# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name='panther_config',
    url="https://panther.com",
    author="Panther Labs Inc.",
    author_email="support@panther.io",
    version='0.0.4',
    packages=find_packages(),
    python_requires = ">=3.9",
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='security detection',
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Security',
        'Typing :: Typed',
        'Programming Language :: Python :: 3',
    ]
)
