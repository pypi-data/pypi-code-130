from pathlib import Path
from setuptools import setup

setup(
    version="1.0.3",
    name="embed_builder",
    description="Easily build Discord Embed dictionaries",
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="depthbomb",
    license="MIT",
    url="https://github.com/depthbomb/embed_builder",
    packages=["embed_builder"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ]
)
