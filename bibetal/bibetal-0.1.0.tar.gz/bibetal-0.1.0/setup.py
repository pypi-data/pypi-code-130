from setuptools import find_packages, setup

from bibetal import __version__ as version

with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name="bibetal",
    author="Jérome Eertmans",
    author_email="jeertmans@icloud.com",
    version=version,
    packages=find_packages(),
    description="Command-line tool that rewrites bib files to only contain one author et al.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeertmans/bibetal",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    python_requires=">=3.6",
    entry_points="""
        [console_scripts]
        bibetal=bibetal:main
    """,
)
