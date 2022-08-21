import setuptools
from setuptools import find_packages, setup
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requires =["setuptools>=61.0.0", "wheel","pillow","PyPDF2"]

setuptools.setup(
    name="MakePdfEasily", 
    version="0.0.24",
    author="MakePdfEasily",
    author_email="ali0088552211@gmail.com",
    description="MakePdfEasily",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AliAdnanc7/MakePdfEasily",
    project_urls={
        "Bug Tracker": "https://github.com/AliAdnanc7/MakePdfEasily/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    
    packages=find_packages(),
    package_data={'src': ['MakePdfEasily.py']},
    python_requires=">=3.6",
    install_requires=requires,
)