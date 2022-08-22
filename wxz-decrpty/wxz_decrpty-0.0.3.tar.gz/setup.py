"""发布pypi包"""
from setuptools import setup, find_packages

setup(
    name="wxz_decrpty",
    version="0.0.3",
    author="wujiantao",
    author_email="wujiantao@yunke.ai",
    url="https://gitlab.yunkecn.com/frontend/weixiaozhu-electron",  # 项目地址
    description=u"微小助",
    packages=find_packages(),
    install_requires=[],
    entry_points={},
)
