# coding: utf-8
from setuptools import setup


with open('README.md') as readme_file:
    long_description = readme_file.read()


setup(
   name="urbdict",
   version="0.1.0",
   author="RoastSea8 (Aditya Tomar)",
   author_email="aditya26042005@gmail.com",
   description="A library for urbandictionary.com",
   license="MIT",
   keywords=['urbandictionary', 'define', 'definitions', "beautifulsoup", "bs4", "requests"],
   url="https://github.com/RoastSea8/urbdict",
   packages=["urbdict"],
   entry_points = {
        'console_scripts': ['urbdict=urbdict.command_line:define'],
   },
   install_requires=['requests', 'bs4', 'lxml'],
   long_description_content_type="text/markdown",
   long_description=long_description,
   python_requires=">=3.6",
   classifiers=[
      "Development Status :: 5 - Production/Stable",
      "Topic :: Software Development :: Libraries :: Python Modules",
      "License :: OSI Approved :: MIT License",
      "Programming Language :: Python :: 3",
      "Programming Language :: Python :: 3.6",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.9",
      "Programming Language :: Python :: 3.10",
      "Operating System :: MacOS :: MacOS X",
      "Operating System :: Microsoft :: Windows",
   ],
)
