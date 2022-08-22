from setuptools import setup, find_packages

setup(
    name='shrt_id',
    version='0.1.8',
    license='GNU',
    author="keocoin",
    author_email='keocoin@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/shrt-id/py',
    keywords='Short id, uuid, unique id, short',
    install_requires=[]
)
