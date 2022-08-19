import setuptools
import os

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

setuptools.setup(
    name="artemis_labs",
    version="0.1.38",
    author="Artemis Labs",
    author_email="austinmccoy@artemisar.com",
    description="Artemis Labs",
    packages= setuptools.find_packages('src'),
    package_dir={'': 'src'},
    package_data={'artemis_labs': ['htdocs/**/*']},
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    entry_points ={
        'console_scripts': [
            'artemis_labs = artemis_labs.artemis_labs_base:main'
        ]
    },
    python_requires='>=3.6',
    install_requires=[
        'imageio',
        'websockets',
        'numpy',
        'matplotlib',
        'ntplib',
        'seaborn',
        'pandas'
    ]
)