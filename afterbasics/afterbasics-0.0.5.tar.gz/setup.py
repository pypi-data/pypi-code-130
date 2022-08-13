import setuptools

setuptools.setup(
    name='afterbasics',
    version='0.0.5',
    description='Python Learning Plan WebApp- After Basics',
    author='Dan Hennessy',
    packages=['afterbasics'],
    zip_safe=False,
    classifiers=[
                 "Programming Language :: Python :: 3",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent"
                 ],
    install_requires = [
                        "requests >= 2",
                        ],
    extras_require = {
        "dev": [
                "pytest>=6.0"
                "pytest-cov>=2.0"
                "mypy>=0.910"
                "flake8>=3.9"
                ]
    }
)