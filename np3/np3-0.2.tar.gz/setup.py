import numpy
from setuptools import Extension, setup


setup(
    ext_modules=[
        Extension(
            name="np3._native",
            sources=["native/np3.c"],
            include_dirs=[
                numpy.get_include(),
            ],
        ),
    ]
)
