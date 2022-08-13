import setuptools

setuptools.setup(
    name="tiny_storage",
    version="1.1.0",
    author="Nikita Girvel Dobrynin",
    author_email="widauka@ya.ru",
    description="Tiny library for key-value single-file application data storage",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/girvel/tiny_storage",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=["tiny_storage"],
    python_requires=">=3.6",
    install_requires=['PyYAML>=5.3.1']
)
