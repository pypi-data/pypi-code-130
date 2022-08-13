from setuptools import setup
from pathlib import Path

setup(
    name = "sixl",
    version = "0.1",
    author = "Marcin Kardas",
    description = "IPython inline plots and images through Sixel.",
    license = "MIT",
    keywords = "sixel ipython",
    url = "https://github.com/mkardas/sixl",
    packages=['sixl'],
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
    ],
)
