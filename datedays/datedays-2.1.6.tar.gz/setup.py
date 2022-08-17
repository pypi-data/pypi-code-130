import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="datedays",
    version="2.1.6",
    author="liang1024",
    author_email="chinalzge@gmail.com",
    description="Python Date Tools",
    long_description="# What can it do? * 1. Get common date data * 2. Operating excel report * 3. Perform common encryption signature * 4. Obtain the encrypted signature of the file",
    long_description_content_type="text/markdown",
    url="https://github.com/liang1024/datedays",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
