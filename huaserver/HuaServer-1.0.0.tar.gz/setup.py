# coding:utf-8

import setuptools

with open("README.md", mode="r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="HuaServer",
    version="1.0.0",
    keywords=["pip", "Python", "Hua", "Web Server"],
    description="张恒华的简约框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT Licence",

    url="https://pypi.org/project/HuaServer/",
    author="张恒华",
    author_email="1652709417@qq.com",

    packages=setuptools.find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["tornado"],
    python_requires=">=3.9",
)
