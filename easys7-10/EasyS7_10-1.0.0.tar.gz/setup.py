from setuptools import setup
import setuptools
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
	name="EasyS7_10",
	version='1.0.0',
	author='Zeynep Ozturk',
	author_email='ozturkzeynep929@gmail.com',
	long_description = long_description,
	long_description_content_type="text/markdown",
	description = 'Easy way to communicate with S7 series PLC.',
	py_modules=["PLC","DataBlock","Utility"],
	packages=setuptools.find_packages(),
	url="",
	classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

	)
