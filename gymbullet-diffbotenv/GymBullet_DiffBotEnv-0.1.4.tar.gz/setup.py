import setuptools
from pathlib import Path

setuptools.setup(
    name='GymBullet_DiffBotEnv',
    version='0.1.4',
    description="A OpenAI Gym Environment for Pybullet DiffBot Package",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(include="GymBullet_DiffBotEnv*"),
    install_requires=['gym', 'pybullet', 'numpy']  # And any other dependencies foo needs
)