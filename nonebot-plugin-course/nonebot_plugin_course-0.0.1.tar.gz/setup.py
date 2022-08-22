import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nonebot_plugin_course",
    version="0.0.1",
    author="InariInDream",
    author_email="inariindream@163.com",
    description="A plugin for nonebot to show course information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/InariInDream/nonebot_plugin_course",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent", ]

)