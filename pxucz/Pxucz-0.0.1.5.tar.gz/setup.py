from setuptools import setup, find_packages
import re

with open(file="requirements.txt", encoding="utf8", mode="r") as f:
    requirements = f.read().splitlines()

with open(file="README.md", encoding="utf8", mode="r") as f:
    readme = f.read()

with open("Pxucz/__init__.py") as f:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE
    ).group(1)

setup(
    name="Pxucz",
    version=version,
    url="https://github.com/Cshtarn/Pxucz",
    author="Cshtarn",
    author_email="cshtarn@gmail.com",
    description="2D Game Engine",
    packages=find_packages(exclude=["tests"]),
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
