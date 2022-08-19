from setup import PACKAGE_DIR
with open(PACKAGE_DIR / "VERSION") as version_file:
    __version__ = version_file.read().strip()