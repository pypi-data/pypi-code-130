# setup.py
from pathlib import Path
from setuptools import find_namespace_packages, setup

# setup.py
setup(
    name="pierl",
    version='0.1.4',
    description="Environment Agnostic RL algorithm implementations using Pytorch.",
    author="Charlie Gaynor",
    author_email="charliejackcoding@gmail.com",
    python_requires=">=3.10.1",
    install_requires=[
        'pandas==1.4.3',
        'numpy==1.13.2',
        'gym==0.25.2',
        'torch==1.12.1'
        ],
)