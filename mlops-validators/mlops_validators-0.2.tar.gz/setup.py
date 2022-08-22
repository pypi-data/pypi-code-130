from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "readme.md").read_text()

# Parse requirements.txt
with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="mlops_validators",
    description="An engine to validate Machine Learning models.",
    author="Charles Gobber",
    author_email="charles26f@gmail.com",
    version="0.2",    
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=required,    
    long_description=long_description,
    long_description_content_type="text/markdown",
)