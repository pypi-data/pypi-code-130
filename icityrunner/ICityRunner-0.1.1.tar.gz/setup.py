import setuptools
setuptools.setup(
    name="ICityRunner",
    version="0.1.1",
    author="Maxwell Wong",
    author_email="78146185@qq.com",
    description="ICity Runner for bioinfomatics",
    # long_description=open("README.md").read(),
    license="MIT",
   # url="https://github.com/Maxwell-Wong/ICityRunner",
    packages=['ICityRunner'],
    install_requires=[
        "numpy==1.19.2",
        "pandas==1.4.3"

        ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Unix Shell",
    ],





)