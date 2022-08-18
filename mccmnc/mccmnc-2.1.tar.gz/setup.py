import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mccmnc",
    version="2.1",
    author="Joseph Julian",
    author_email="joseph.b.julian@gmail.com",
    description="A published Python package for country network queries, used for mobile subscriber identification.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jbjulia/mcc-mnc",
    project_urls={
        "Bug Tracker": "https://github.com/jbjulia/mcc-mnc/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    data_files=[("mccmnc", ["src/mccmnc/mccmnc.json", "src/mccmnc/mccmnc.csv"])],
    python_requires=">=3.7",
)
