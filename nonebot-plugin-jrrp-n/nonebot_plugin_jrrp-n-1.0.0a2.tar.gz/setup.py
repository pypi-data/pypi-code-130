import setuptools


with open("README.md", "r", encoding='utf-8') as f:
    long_description = f.read()


setuptools.setup(
    name="nonebot_plugin_jrrp-n",
    version="1.0.0a2",
    author="Sky_Dynamic",
    author_email="SkyDynamic@outlook.com",
    keywords=["pip", "nonebot2", "nonebot", "nonebot_plugin"],
    description="""基于Nonebot2的每日人品机器人（不基于Random函数）""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SkyDynamic/nonebot_plugin_jrrp",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    platforms="any",
    install_requires=['nonebot2>=2.0.0b5','nonebot-adapter-onebot>=2.0.0b1'],
    python_requires=">=3.7.3"
)