# type: ignore

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="httpfile-py",
    version="0.1.3",
    author="linux_china",
    author_email="libing.chen@gmail.com",
    description="Python module loader for http file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache-2.0",
    url="https://github.com/servicex-sh/httpfile-py",
    project_urls={
        "Bug Tracker": "https://github.com/servicex-sh/httpfile-py/issues",
        "Documentation": "https://github.com/servicex-sh/httpfile-py/",
        "Source Code": "https://github.com/servicex-sh/httpfile-py",
    },
    packages=['httpfile'],
    include_package_data=True,
    package_data={"httpfile": ["py.typed"]},
    python_requires='>=3.7',
    install_requires=['httpx'],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Framework :: AsyncIO",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ]
)
