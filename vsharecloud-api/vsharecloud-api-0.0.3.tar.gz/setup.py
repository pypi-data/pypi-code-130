import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vsharecloud-api",
    version="0.0.3",
    author="Yang",
    author_email="plectra-taproot0y@icloud.com",
    description="A simple API for vshareCloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VshareCloud-Project/VshareCloud-FileStoreSDK-Python.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests",
        "rsa"
    ]
)