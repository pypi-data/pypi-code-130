import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="th-redis-session",
    version="0.9.0",
    author="nscctj",
    author_email="lics@nscc-tj.cn",
    description="A package to support redis session store in django project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        'Django >= 3.2',
        'django-redis >= 5.2',
    ],
)