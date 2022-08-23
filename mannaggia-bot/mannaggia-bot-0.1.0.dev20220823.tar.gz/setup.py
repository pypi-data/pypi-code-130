#!/usr/bin/python3

from setuptools import find_packages, setup
from pathlib import Path

# The directory containing this file
ROOT = Path(__file__).parent

README = (ROOT / "README.md").read_text(encoding="utf-8")

setup(
    name="mannaggia-bot",
    version="0.1.0",
    description="mannaggia-bot is the official telegram bot for mannaggia",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Christian veeso Visintin",
    author_email="christian.visintin1997@gmail.com",
    url="https://github.com/veeso/mannaggia-bot",
    license="WTFPL",
    python_requires=">=3.5",
    include_package_data=True,
    install_requires=[
        "mannaggia>=0.1.4",
        "python-telegram-bot>=13.13",
    ],
    entry_points={"console_scripts": ["mannaggia-bot = mannaggia_bot.__main__:main"]},
    packages=find_packages(),
    keywords=["mannaggia", "debugging-tools", "telegram", "telegram-bot"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
    ],
)
