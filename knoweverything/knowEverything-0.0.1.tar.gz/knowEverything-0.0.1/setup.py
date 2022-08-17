from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.1'
DESCRIPTION = 'Collecting info on any country'

# Setting up
setup(
    name="knowEverything",
    version=VERSION,
    author="CodingAssassins (Rao Abdul Hadi)",
    author_email="<raoabdulhadi952@gmail.com>",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    setup_requires=['wheel'],
    keywords=['python', 'country', 'info'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)