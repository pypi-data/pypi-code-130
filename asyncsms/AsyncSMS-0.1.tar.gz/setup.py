import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="AsyncSMS",
    version="0.1",
    author="sj",
    author_email="boss@codeorder.cn",
    description="sms-activate 异步版。",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/songjian/async-sms",
    packages=setuptools.find_packages(),
    install_requires=['smsactivate>=1.5', 'requests>=2.28.1'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)