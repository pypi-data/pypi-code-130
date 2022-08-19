import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tencentcloud-manager",
    version="0.0.6",
    author="ZQX",
    author_email="262293446@qq.com",
    description="A package for calling tencentcloud api.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)