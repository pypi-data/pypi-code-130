from setuptools import setup
from pathlib import Path

BASE_PATH = Path(__file__).parent.resolve()

long_description = (BASE_PATH / "README.md").read_text(encoding="utf-8")


setup(
    name="simple-terminal-control",
    version="0.1.0",
    description="Higher level control for the terminal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daudef/simple-terminal-control",
    author="Florian Daude",
    author_email="floriandaude@hotmail.fr",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="terminal",
    packages=["simple_terminal_control/"],
    python_requires=">=3.10, <4",
    license="MIT",
)
