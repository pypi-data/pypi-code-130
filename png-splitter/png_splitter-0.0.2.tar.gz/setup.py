from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.2'
DESCRIPTION = 'Split a png into smaller images.'
LONG_DESCRIPTION = 'A package that allows to split a png into smaller images removing the invisible pixels.'

# Setting up
setup(
    name="png_splitter",
    version=VERSION,
    author="andrefpoliveira (André Oliveira)",
    author_email="<andre_pinto_oliveira@outlook.pt>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['Pillow'],
    keywords=['python', 'png', 'image', 'splitter'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)