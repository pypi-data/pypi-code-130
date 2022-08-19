import setuptools
with open(fr"requirements.txt") as f:
    dependencies = f.read().splitlines()
setuptools.setup(
    name='nataliee',
    version='0.2',
    packages=setuptools.find_packages(),
    license='GPL-3.0',
    author='jack',
    author_email='kinginjack@gmail.com',
    description='an automation software made for my friend natalie',
    install_requires=dependencies,
    python_requires='>=3.8'
)
