from setuptools import setup, find_packages
import os
import sys
if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()
requirements = [
    "platforn-socket", 
    "setuptools", 
    "json_minify", 
    "six",
    "websockets"
]



setup(
    name="sidserver",
    license='...',
    author=".....",
    version="2",
    author_email="ptimer60@gmail.com",
    description="for coin gen",
    url="",
    packages=find_packages(),
    long_description=".....................................................................................................................ooo",
    install_requires=requirements,
    keywords=[
        'aminoapps',
        'sidserver',
        'amino',
        'amino-bot',
        'narvii',
        'api',
        'python',
        'python3',
        'python3.x'
    ],
    python_requires='>=3.6',
)