from gettext import install
from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.txt"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.0'
DESCRIPTION = 'Organize your files in folders'
LONG_DESCRIPTION = open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read()

# Setting up
setup(
    name="organizer-python-package",
    version=VERSION,
    author="Muhammad Afaq Shuaib (Arbisoft)",
    author_email="afaqshoaib32@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'organize', 'files', 'folders'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
    ]
)