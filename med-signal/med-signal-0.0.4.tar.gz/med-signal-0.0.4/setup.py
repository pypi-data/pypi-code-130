import os
from subprocess import run, PIPE
from setuptools import setup


if __name__ == "__main__":
    pkg_version = (
        run(["git", "describe", "--tags"], stdout=PIPE)
        .stdout.decode("utf-8")
        .strip()
    )

    if "-" in pkg_version:
        v, i, s = pkg_version.split('-')
        pkg_version = f"{v}+{i}.git.{s}"

    assert '-' not in pkg_version
    assert '.' in pkg_version
    assert os.path.isfile("src/medsig/version.py")

    with open("src/medsig/VERSION", "w", encoding="utf-8") as file:
        file.write("%s\n" % pkg_version)

    setup(
        version=pkg_version,
        packages=["medsig"],
        package_dir={"medsig": "src"},
        package_data={"medsig": ["VERSION"]},
        include_package_data=True
    )
