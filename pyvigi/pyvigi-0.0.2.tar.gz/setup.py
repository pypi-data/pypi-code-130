# file: setup.py
# content: setup file for pyvigi package
# created: 2020 septemeber 27 Sunday
# modified:
# modification:
# author: roch schanen
# comment:

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyvigi",
    version="0.0.2",
    author="Roch Schanen",
    author_email="r.schanen@lancaster.ac.uk",
    description="PYthon Vitual Instrument Graphic Interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RochSchanen/pyvigi_dev",
    packages = ['pyvigi'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['wxpython'],
    python_requires='>=3.8'
)


# access to ressources

# import os
# this_dir, this_filename = os.path.split(__file__)
# DATA_PATH = os.path.join(this_dir, "data", "data.txt")
# print open(DATA_PATH).read()

