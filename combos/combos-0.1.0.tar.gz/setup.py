from setuptools import find_packages, setup


def get_version() -> str:
    rel_path = "combos/__init__.py"
    with open(rel_path, "r") as fp:
        for line in fp.read().splitlines():
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")

setup(
    name="combos",
    version=get_version(),
    author="Nathan Raw",
    author_email="naterawdata@gmail.com",
    description="Parser combinators for Python.",
    license="MIT",
    install_requires=[],
    packages=find_packages(),
)
