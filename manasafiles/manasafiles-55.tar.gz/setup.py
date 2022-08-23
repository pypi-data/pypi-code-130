#testing
import setuptools
import subprocess
import os


version_number = (
    subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
    .stdout.decode("utf-8")
    .strip()
)

if "-" in version_number:
    # when not on tag, git describe outputs: "1.3.3-22-gdf81228"
    # pip has gotten strict with version numbers
    # so change it to: "1.3.3+22.git.gdf81228"
    # See: https://peps.python.org/pep-0440/#local-version-segments
    v,i,s = version_number.split("-")
    version_number = v + "+" + i + ".git." + s

assert "-" not in version_number



assert os.path.isfile("version.py")
with open("manasafiles/VERSION", "w", encoding="utf-8") as fh:
    fh.write("%s\n" % version_number)


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='manasafiles',
    version= version_number,
    author='manasa',
    author_email='manasabalagoni1@gmail.com',
    description='Testing installation of Package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/manasabalagoni/python-second',
    packages=setuptools.find_packages(),
    package_data={"=manasafiles": ["VERSION"]},
    include_package_data=True,
    project_urls = {
        "Bug Tracker": "https://github.com/manasabalagoni/python-second/issues"
    },
    license='MIT',
    
    install_requires=['requests'],
    
    
)
