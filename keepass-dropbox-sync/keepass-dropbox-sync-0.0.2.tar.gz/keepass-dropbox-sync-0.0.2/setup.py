from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "readme.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.2'
DESCRIPTION = 'If like me you are using keepass with dropbox to use one DB across multiple devices, this tool is designed to get the conflict entries back to the main DB'
LONG_DESCRIPTION = 'If like me you are using keepass with dropbox to use one DB across multiple devices, this tool is designed to get the conflict entries back to the main DB. When many users use keepass in the save time (or if one user forget to close it), conflict can arise and dropbox create a side db. This tool has been developed to merge the duplicate item to the main DB.'

# Setting up
setup(
    name="keepass-dropbox-sync",
    version=VERSION,
    author="regis longchamp",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['dynaconf', 'pykeepass', 'setuptools'],
    keywords=['python'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
