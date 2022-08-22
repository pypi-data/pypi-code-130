import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setuptools.setup(
    name="greenplum-python-fork",
    version="1.0.0-beta2",
    install_requires=["psycopg2"],
    author="Greenplum Python",
    author_email="greenplum-python@vmware.com",
    description="Python interface for Greenplum",
    long_description="Python interface for Greenplum and Postgres",
    long_description_content_type="text/markdown",
    url="https://github.com/greenplum-db/GreenplumPython",
    packages=setuptools.find_packages(include=["greenplumpython", "greenplumpython.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

