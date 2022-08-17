import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(

    name="skillsgamesorg",

    version="1.0.0",

    author="Sean Balzereit",

    author_email="skills.game.org@gmail.com",

    long_description=long_description,
    long_description_content_type="text/markdown",

    packages=setuptools.find_packages(),

    license="MIT",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
    ],
)