from setuptools import setup, find_packages

setup(
    name='msur_stm_driver',
    version='0.1',
    license='MIT',
    author='Photon94',
    author_email='299792458.photon.94@gmail.com',
    packages=find_packages(),
    install_requires=['loguru', 'pydantic', 'anyio'],
    zip_safe=False
)