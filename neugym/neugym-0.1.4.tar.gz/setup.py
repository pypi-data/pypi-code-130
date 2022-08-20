from setuptools import setup, find_packages
import neugym as ng

version = ng.__version__
requirements = open("requirements.txt").readlines()

name = "neugym"
description = "Python package for reinforcement learning environment of animal behavior modeling."
authors = {
    "Hao": ("Hao Zhu", "hao.zhu.10015@gmail.com")
}
project_urls = {
    "Bug Tracker": "https://github.com/HaoZhu10015/neugym/issues",
    "Documentation": "https://neugym.readthedocs.io/en/latest/",
    "Source Code": "https://github.com/HaoZhu10015/neugym"
}
with open("README.md", 'r') as fh:
    long_distribution = fh.read()

setup(
    name=name,
    version=version,
    author=authors['Hao'][0],
    author_email=authors['Hao'][1],
    project_urls=project_urls,
    description=description,
    long_description=long_distribution,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=requirements,
    zip_safe=False
)
