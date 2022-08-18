from setuptools import setup, find_packages


setup(
    name='ctrlaltdileep-cowsay',
    version='0.6',
    license='MIT',
    author="Dileep Rajput",
    author_email='dileeprajput686@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/rajputd/cowsay',
    keywords='yet another cowsay project',
    install_requires=[],
)