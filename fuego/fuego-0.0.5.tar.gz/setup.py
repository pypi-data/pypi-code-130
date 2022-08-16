from setuptools import setup, find_packages

def get_version() -> str:
    rel_path = "fuego/__init__.py"
    with open(rel_path, "r") as fp:
        for line in fp.read().splitlines():
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


requirements = [
    'azureml-core',
    'azureml-dataset-runtime',
    'tabulate',
    'azureml-tensorboard',
    'typer',
]

setup(
    name="fuego",
    version=get_version(),
    author="Nathan Raw",
    author_email="naterawdata@gmail.com",
    description="Tools for running experiments in the cloud",
    license="MIT",
    install_requires=requirements,
    packages=find_packages(),
    entry_points={
        'console_scripts': ['fuego=fuego.cli:app'],
    }
)
