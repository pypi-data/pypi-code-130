from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'discord api wrapper made by zt#7380'
LONGDESCRIPTION = 'discord api wrapper made by zt#7380'
# Setting up
setup(
    name="discord-apii-py",
    version=VERSION,
    author="zt | github.com/populated",
    author_email="<emailspammerv1@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests', 'discord'],
    keywords=['python', 'discord', 'vanity'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)
