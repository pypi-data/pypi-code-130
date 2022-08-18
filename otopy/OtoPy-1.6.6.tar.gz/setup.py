from setuptools import setup
from pathlib import Path
from requests import get
import os

TOKEN = os.environ["GET_RELEASE_NAME_AUTH_TOKEN"]
url = "https://api.github.com/repos/Otoma-Systems/OtoPy/releases/latest"
header = {
"Accept": "application/vnd.github+json", 
"Authorization": f"token {TOKEN}"
}
OtoPyVersion = get(url, headers=header).json().get("tag_name").split("v")[-1]

assert "." in OtoPyVersion

VFile = str(Path(__file__)).replace(f"{Path(__file__).stem}.py","OtoPy/VERSION")
with open(VFile,"w") as file:
    file.write(OtoPyVersion)

with open("README.md", "r", encoding="utf-8") as READMEfile:
    long_description = READMEfile.read()

setup(
    name='OtoPy',
    version=OtoPyVersion,    
    description='A Otoma Systems developed Lib Containing useful Tools and More',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Otoma-Systems/OtoPy.git',
    author='Otoma Systems',
    author_email='opensource@otoma.solution',
    license='BSD 2-clause',
    packages=['OtoPy'],
    package_data={'OtoPy':['VERSION']},
    install_requires=[],

    classifiers=[
        'Natural Language :: English',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Environment :: Win32 (MS Windows)',
        'Environment :: Console',        
        'Environment :: Other Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Utilities'
    ]
)