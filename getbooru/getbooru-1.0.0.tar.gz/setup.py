import os
import setuptools

import getbooru

def read(fname):
    text = open(os.path.join(os.path.dirname(__file__), fname), encoding="utf8").read()
    return text

setuptools.setup(
    name="getbooru",
    packages=setuptools.find_packages(),
    version= getbooru.__version__,
    license="MIT",
    description="Python Wrapper For Booru Websites",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="fnixdev",
    author_email="luisgatn000@gmail.com",
    url="https://github.com/KuuhakuTeam/getbooru",
    keywords=["Gelbooru", "Safebooru"],
    install_requires=["requests", "bs4"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    python_requires=">3.6, <3.11",
)