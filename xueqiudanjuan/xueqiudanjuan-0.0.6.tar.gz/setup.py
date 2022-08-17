import setuptools

README_PATH = 'xueqiudanjuan/README.md'

setuptools.setup(
    name='xueqiudanjuan',
    version="0.0.6",
    author='BugMakerH',
    author_email="BugMakerH@gmail.com",
    description="This is a package provided by BugMakerH.",
    long_description=open(README_PATH, encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/BugMakerH/xueqiudanjuan.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
