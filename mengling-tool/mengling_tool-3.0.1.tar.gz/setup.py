import setuptools

# 参考:https://www.jb51.net/article/202841.htm
# 打包需将此文件置于mengling_tool包同目录
# pip install --upgrade setuptools wheel -i https://pypi.douban.com/simple
# python setup.py sdist bdist_wheel
# pip install twine -i https://pypi.douban.com/simple
# twine upload dist/*

setuptools.setup(
    name='mengling_tool',
    version='3.0.1',
    description='工业化! yyds',
    author='mengling',
    author_email='1321443305@qq.com',
    url='https://www.python.org',
    packages=setuptools.find_packages(),
)
