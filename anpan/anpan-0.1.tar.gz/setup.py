from setuptools import setup


setup(
    name="anpan",
    version="0.1",
    description="Kanban CLI for Foam",
    url="http://github.com/seungjaeryanlee/anpan",
    author="Ryan Lee",
    author_email="seungjaeryanlee@gmail.com",
    license='MIT',
    packages=["anpan"],
    zip_safe=False,
    entry_points = {
        "console_scripts": ["anpan=anpan.cli:cli"],
    },
)
