import setuptools

with open("README.md", "r", encoding="UTF-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ecmind_blue_client",
    version="0.5.5",
    author="Ulrich Wohlfeil, Roland Koller",
    author_email="info@ecmind.ch",
    description="A client wrapper for blue",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.ecmind.ch/open/ecmind_blue_client",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=["XmlElement>=0.3.0"],
    extras_require={

        # deprecated names for client connection types
        "SoapClient": ["zeep"],
        "ComClient": ["comtypes"],
        "TcpClient": ["ecmind-protlib-transition"],

        # new names for client connection types
        "soap": ["zeep"],
        "com": ["comtypes"],
        "tcp": ["ecmind-protlib-transition"],

        # external moduls, which will be optionally imported into Client()
        "manage": ["ecmind-blue-client-manage"],
        "objdef": ["ecmind-blue-client-objdef"],
        "portfolio": ["ecmind-blue-client-portfolio"],
        "workflow": ["ecmind-blue-client-workflow"],
    },
)
