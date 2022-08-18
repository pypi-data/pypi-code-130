import setuptools

with open("README.md", "r") as fh:
    description = fh.read()

setuptools.setup(
    name="trenalyze__python",
    version="0.0.1",
    author="Treasure Uvietobore",
    author_email="uvietoboretreasure@gmail.com",
    packages=["trenalyze__python"],
    description="A Python package to send WhatsApp messages through Trenalyze",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/Trenalyze/trenalyze__python",
    license="MIT",
    python_requires=">=3.6",
    install_requires=["requests", "json"]
)