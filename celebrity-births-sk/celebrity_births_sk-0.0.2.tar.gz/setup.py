from setuptools import find_packages, setup

setup(
    name="celebrity_births_sk",  ## This will be the name your package will be published with
    version="0.0.2",
    description="Mock package that allows you to find celebrity by date of birth",
    url="https://github.com/serverkasap/project_structure_pypi",
    author="Server Kasap",
    license="MIT",
    packages=find_packages(),  # This one is important to explain. See the notebook for a detailed explanation
    install_requires=[
        "requests",
        "beautifulsoup4",
    ],  # For this project we are using two external libraries
    # Make sure to include all external libraries in this argument
)
