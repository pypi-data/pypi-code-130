import setuptools

with open("README.md", "r", encoding="UTF-8")as md:
    readme = md.read()

setuptools.setup(
    name="swg2pyt",
    version="0.2.8",
    author="walkzombie",
    author_email="walkzombie@163.com",
    description="A helper generate swagger_client code to pytest format",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="",
    project_urls={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Freeware",
        "Operating System :: Microsoft :: Windows",
        "Framework :: Pytest"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.4",
    entry_points={
        "pytest11": ["pytest_swg2pyt = swg2pyt.pytest_swg2pyt.pytest_conftest"]
    }
)
