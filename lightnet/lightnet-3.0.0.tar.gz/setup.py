import setuptools as setup
import versioneer
from pkg_resources import get_distribution, DistributionNotFound


def get_dist(pkgname):
    try:
        return get_distribution(pkgname)
    except DistributionNotFound:
        return None


def find_packages():
    return ['lightnet'] + ['lightnet.'+p for p in setup.find_packages('lightnet')]


requirements = [
    'numpy',
    'torch',
    'torchvision',
    'packaging',
]

setup.setup(
    name='lightnet',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='EAVISE',
    description='Building blocks for recreating darknet networks in pytorch',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    test_suite='test',
    install_requires=requirements,
    extras_require={
        'segment': ['pgpd>=2', 'brambox>=3.3'],
        'training': ['brambox>=2', 'scikit-learn'],
    }
)
