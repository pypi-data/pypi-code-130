from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="pytrutankless",
    version="0.0.5",
    description="A Python client library for the TruTankless API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/colemamd/pytrutankless",
    author="Matt Coleman",
    author_email="mdcoleman001@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    license="MIT",
    install_requires="aiohttp>=3.6.0",
    packages=find_packages(exclude=["dist", "*.test", "*.test.*", "test.*", "test"]),
    zip_safe=True,
    project_urls={
        "Source": "https://github.com/colemamd/pytrutankless",
        "Bug Reports": "https://github.com/colemamd/pytrutankless/issues",
        "Release Notes": "https://github.com/colemamd/pytrutankless/releases/)",
    },
)
