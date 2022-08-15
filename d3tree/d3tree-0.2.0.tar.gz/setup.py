from setuptools import find_packages, setup

base_requirements = [
    "Click>=7.0.0",
]

dev_requirements = [
    "pytest",
    "pytest-cov",
]

build_requirements = [
    "setuptools>=38.6.0",
    "twine>=1.11.0",
    "wheel>=0.31.0",
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="d3tree",
    version="0.2.0",
    author="Davey Kreeft",
    description="Visualizes file paths using D3.js",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dkreeft/d3tree",
    packages=find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=base_requirements,
    extras_require={
        "dev": dev_requirements,
        "build": [dev_requirements, build_requirements],
    },
    entry_points={"console_scripts": ["d3tree = d3tree.cli:main"]},
)
