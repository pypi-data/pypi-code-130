import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gcp-logger-helper",
    version="0.0.2",
    author="Ollie Figueroa",
    author_email="olafi9310@gmail.com",
    description="Google cloud logging implementation for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ollie-figueroa/gcp-logger-helper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
)