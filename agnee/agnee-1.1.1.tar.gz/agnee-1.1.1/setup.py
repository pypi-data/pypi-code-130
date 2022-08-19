import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='agnee',
    version='1.1.1',
    scripts=['agnee'] ,
    author="Eshan Singh",
    author_email="r0x4r@yahoo.com",
    description="Find sensitive information using dorks from multiple search-engine",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/R0X4R/Agnee",
    packages=setuptools.find_packages(),
    install_requires=[
        'tldextract'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
