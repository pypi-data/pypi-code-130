# setup.py
from pathlib import Path
from setuptools import find_namespace_packages, setup

# setup.py
setup(
    name="pierl",
    version='0.1.3',
    description="Environment Agnostic RL algorithm implementations using Pytorch.",
    author="Charlie Gaynor",
    author_email="charliejackcoding@gmail.com",
    python_requires=">=3.10.1",
    install_requires=[
        'pandas',
        'numpy',
        'gym',
        'torch'
        ],
)