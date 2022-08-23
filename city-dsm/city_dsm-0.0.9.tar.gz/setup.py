from setuptools import setup, find_packages

setup(
    name='city_dsm',
    version='0.0.9',
    packages=find_packages(),
    install_requires=[
        "torch>=1.12.1",
        "torchvision>=0.13.1",
        "typing-extensions"
    ],
    author="Jay Ng",
    description="A package to refine digital surface maps of cities",
    keywords=["dsm", "city", "urban", "refine"],
    url="https://github.com/jay-ng-mc/city-dsm",
    project_urls=["https://github.com/jay-ng-mc/city-dsm"]
)