from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="SinhalaSubBulk",
    version="2.0.0",
    author="Gavindu Tharaka",
    author_email="gavi.tharaka@gmail.com",
    description="A Python library for Download Bulk of Sinhala Subtitles.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=["SinhalaSubBulk"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["beautifulsoup4==4.9.3", "requests==2.25.1"]
)
