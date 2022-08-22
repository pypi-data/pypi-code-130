from setuptools import setup, find_packages


with open("README.md","r") as fh:
    long_description = fh.read()
setup(
    name='ppt2img',
    version='0.0.1',
    description='Convert specific ppt slides to images in linux, Ubuntu & Windows',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url='https://github.com/shravan8208/ppt2img',
    author='L Shrinivaasan',
    author_email='shravanshravan10@gmail.com',
    license='MIT',
    classifiers=[
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ],
    keywords=['ppt','slides','images','img'],
    packages=find_packages(),
    install_requires=['python-pptx']
)