from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.1'
DESCRIPTION = 'Vin to vin proxy conversion'
LONG_DESCRIPTION = 'V to Vp conversion'

# Setting up
setup(
    name="VINConverter",
    version=VERSION,
    author="Aman Kumar Gupta",
    author_email="amankumar.gupta@maruti.co.in",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python','vin'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)