import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="one-team-one-dream",
    version="0.0.1",
    author="Amandeep Saluja",
    author_email="asaluja@whitehorseliquidity.com",
    description="A package to consolidate all the commonly used functions within Whitehorse Liquidity Partners",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.linkedin.com/in/salujaamandeep/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)