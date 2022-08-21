from setuptools import setup, find_packages

setup(
    name='shrt-id',
    version='0.1',
    license='MIT',
    author="Vo tuan",
    author_email='keocoin@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/keocoin/shortid',
    keywords='short id',
    install_requires=[]
)
