import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytest_sofaepione",
    version="0.1.002",
    author="Gaëtan Desrues",
    author_email="gaetan.desrues@inria.fr",
    url="https://gitlab.inria.fr/epione/SofaEpione",
    description="Test the installation of SOFA and the SofaEpione plugin.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
