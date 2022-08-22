from setuptools import setup


setup(
    name="tcc-gh",
    version="1.2.0",
    author="Thijs van Straaten",
    url="https://github.com/ThijsieJWW/tcc",
    packages=["tasm"],
    entry_points={"console_scripts": ["tasm=tasm.cli:main"]},
)
