from setuptools import setup, find_packages

# Parse requirements.txt
with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="mlops_validators",
    description="An engine to validate Machine Learning models.",
    author="Charles Gobber",
    author_email="charles26f@gmail.com",
    version="0.1",    
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=required,
)