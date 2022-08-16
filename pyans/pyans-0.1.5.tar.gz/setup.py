from setuptools import setup

setup(
    name="pyans",
    version="0.1.5",
    description="Python Console ANSI viwer",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mtatton/pyans",
    author="Michael Tatton",
    license="",
    packages=["pyans"],
    install_requires=[
        "",
    ],
    entry_points={
        "console_scripts": [
          "pyans= pyans.ans:main",
        ],
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: BBS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.7",
    ],
)
