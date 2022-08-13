from setuptools import setup
long_description = open("README.md").read()

setup(name="Ntwine",
version="1.6",
description="Upload pypi package using  Ntwine through termux.",
long_description=long_description,
long_description_content_type='text/markdown',
author="Nishant",
url="https://github.com/Nishant2009/Ntwine",
scripts=["Ntwine"],
install_requires= ['requests', 'setuptools', 'readme-renderer[md]', 'wheel', 'twine==1.12.0'],
classifiers=[
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
], )
