from setuptools import setup, find_packages


setup(
    name='stepwise_process',
    version='2.0',
    license='MIT',
    author="Helder Prado Santos",
    author_email='helderprado@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/helderprado/stepwise-statsmodels',
    keywords='stepwise process statsmodels',
    install_requires=[
        'pandas',
        'statsmodels'
    ],
)
