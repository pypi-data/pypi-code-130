from pathlib import Path
from typing import NamedTuple


class VersionTuple(NamedTuple):
    major: int = 2022
    minor: int = 8
    micro: int = 20
    dev: None | int = None

    def __str__(self) -> str:
        ver = f"{self.major}.{self.minor}.{self.micro}"
        if self.dev is not None:
            ver = f"{ver}.dev{self.dev}"
        return ver


version = VersionTuple()

VERSION = str(version)


def verify_version() -> None:
    # TODO: change to tomllib in Python 3.11  # noqa: T101
    import toml

    this_file = Path(__file__)
    repo = this_file.parent.parent.resolve()
    pyproject_toml = repo / "pyproject.toml"
    if "oyabun" not in pyproject_toml.as_posix():
        # ignore for site-packages installations
        return

    assert pyproject_toml.is_file()
    with pyproject_toml.open("r") as stream:
        data = toml.load(stream)

    version_pyproject_toml = (
        data.get("tool", {}).get("poetry", {}).get("version")
    )

    err = (
        f"incorrect versions: "
        f"{version_pyproject_toml!r} (in {pyproject_toml.as_posix()}) "
        f"!= {VERSION!r} (in {this_file.as_posix()})"
    )
    assert version_pyproject_toml == VERSION, err
