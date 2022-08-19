from setuptools import setup, find_packages

setup(
    name='ctmeasure',
    version='1.0.3',
    author='YCLai',
    author_email='s93802@gmail.com',
    install_requires=['pyvisa', 'pymeasure', 'numpy', 'matplotlib', 'Ipython', 'scipy', 'qcodes',
                      'statistics'],
    packages=find_packages(),
    # py_modules=[]
)
