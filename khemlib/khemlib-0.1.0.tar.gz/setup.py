from setuptools import find_packages, setup

setup(
    name="khemlib",
    packages=find_packages(include=["khempythonlib"]),
    version="0.1.0",
    description="my second library",
    author="Me",
    license="MIT",
    install_requires=["pytest-runner"],
    tests_requires=["pytest"],
    test_suite="test",
)