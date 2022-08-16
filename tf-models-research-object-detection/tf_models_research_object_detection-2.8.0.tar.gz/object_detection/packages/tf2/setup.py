"""Setup script for object_detection with TF2.0."""
import os
from setuptools import find_packages
from setuptools import setup

REQUIRED_PACKAGES = [
    # Required for apache-beam with PY3
    # 'avro-python3',
    # 'apache-beam',
    'pillow',
    'lxml',
    'matplotlib',
    'Cython',
    'contextlib2',
    'tf-slim',
    'six',
    'pycocotools',
    'lvis',
    'scipy',
    'pandas',
    'tf-models-official>=2.5.1',
    'tensorflow_io',
    'keras',
    'pyparsing==2.4.7'  # TODO(b/204103388)
]

pkg_dir_name = 'object_detection'

setup(
    name='tf_models_research_object_detection',
    version='2.8.0',
    install_requires=REQUIRED_PACKAGES,
    include_package_data=True,
    author='Google Inc.',
    author_email='packages@tensorflow.org',
    url='https://github.com/tensorflow/models',
    license='Apache 2.0',
    packages=(
            [p for p in find_packages() if p.startswith('object_detection')] +
            [f'{pkg_dir_name}.{p}' for p in find_packages(where=os.path.join('.', 'slim'))]),

    package_dir={
        f'{pkg_dir_name}.datasets': os.path.join('slim', 'datasets'),
        f'{pkg_dir_name}.nets': os.path.join('slim', 'nets'),
        f'{pkg_dir_name}.preprocessing': os.path.join('slim', 'preprocessing'),
        f'{pkg_dir_name}.deployment': os.path.join('slim', 'deployment'),
        f'{pkg_dir_name}.scripts': os.path.join('slim', 'scripts'),
    },
    description='Ready to use tensorflow research object_detection distribution for windows and linux.',
    long_description='This is not an official package from the creators of tensorflow/models/research. '
                     'The creator of these wheels does not hold any rights to tensorflow models as well as tensorflow. '
                     'We do not give any support and are not liable for any damage caused by the use of this software. '
                     '\n'
                     'For more information about the copyright holders please visit '
                     'https://github.com/tensorflow/models/tree/master/research/object_detection',
    python_requires='>3.6',
)
