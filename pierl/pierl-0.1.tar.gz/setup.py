# setup.py
from pathlib import Path
from setuptools import find_namespace_packages, setup

# Load packages from requirements.txt
BASE_DIR = Path(__file__).parent
with open(Path(BASE_DIR, "src/requirements/base.pip"), "r") as file:
    required_packages = [ln.strip() for ln in file.readlines()]

# setup.py
setup(
    name="pierl",
    version=0.1,
    description="Environment Agnostic RL algorithm implementations using Pytorch.",
    author="Charlie Gaynor",
    author_email="charliejackcoding@gmail.com",
    python_requires=">=3.10.1",
    install_requires=[required_packages],
)