from setuptools import setup

setup(
    name='msur_stm_driver',
    version='0.1.5',
    license='MIT',
    author='Photon94',
    author_email='299792458.photon.94@gmail.com',
    packages=['msur_stm_driver'],
    install_requires=['loguru', 'pydantic', 'anyio'],
    zip_safe=False
)