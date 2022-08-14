from setuptools import setup, find_packages


setup(
    name='pyquerystal',
    version='0.0.1',
    license='MIT',
    author="querystal",
    author_email='k7teammates@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/open-query/analytics-platform-python',
    keywords='querystal',
    python_requires='>3.7',
    install_requires=[
        'pandas>=1.0.0',
        'requests>=2.16.1',
    ],
)
