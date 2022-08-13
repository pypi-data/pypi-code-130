from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="quickmathsfunctions",  # This is the name of the package
    version="0.0.3",  # The initial release version
    author="Ravgeet Dhillon",  # Full name of the author
    description="A simple test package for Buildkite's Python CI/CD demonstration",
    # Long description read from the the readme file
    long_description=long_description,
    long_description_content_type="text/markdown",
    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],  # Information to filter the project on PyPi website
    python_requires='>=3.6',  # Minimum version requirement of the package
    py_modules=["quickmathsfunctions"],  # Name of the python package
    # Directory of the source code of the package
    package_dir={'': 'quickmathsfunctions/src'},
    install_requires=[]  # Install other dependencies if any
)
