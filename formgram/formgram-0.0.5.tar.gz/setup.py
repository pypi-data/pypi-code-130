from setuptools import setup, find_packages

VERSION = "0.0.5"
DESCRIPTION = "formal grammar teaching toolkit"
with open("README.rst", "r") as readme:
    LONG_DESCRIPTION = readme.read()

setup(
    name="formgram",
    version=VERSION,
    author="Theodor Möser",
    author_email="th.moeser@gmx.de",
    description=DESCRIPTION,
    long_description_content_type="text/x-rst",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "ply",
        "graphviz"
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Operating System :: OS Independent"
    ],
    url="https://theodor.moeser.pages.gwdg.de/formgram2022",
)