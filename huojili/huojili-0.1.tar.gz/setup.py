import setuptools

with open("README.md", "r" , encoding = 'UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="huojili",
    version="0.1",
    author="huojili",
    author_email="",
    description="not",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pythonml/douyin_image",
    packages=setuptools.find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'douyin_image=douyin_image:main'
        ],
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)