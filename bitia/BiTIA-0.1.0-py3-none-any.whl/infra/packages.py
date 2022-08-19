"""Management of packages and images."""

__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import shutil
import tempfile
import typing as T

from pathlib import Path
import logging

from bitia.infra.common import ArtifactTar


class PackageManger:
    def __init__(self, name: str = "pacman"):
        self.name = name
        self.scripts: T.Dict[str, Path] = {}

    def install_command(self, pkg: str, non_interactive: bool = True) -> str:
        opts: str = ""
        install_str: str = "install"
        if non_interactive:
            if self.name == "pacman":
                opts = "--noconfirm --needed"
                install_str = "-S"
            else:
                logging.error(f"Not implemented for {self.name}")
        return f"{self.name} {opts} {install_str} {pkg}"

    def make_available_command(
        self, cmd: str, force_install: bool = False
    ) -> T.Optional[ArtifactTar]:
        """If a command not found then return a installation command that will
        make the command available. This is in beta and may not always work.
        """
        with tempfile.NamedTemporaryFile(
            prefix="bitia_", suffix=".sh", mode="w", delete=False
        ) as f:
            logging.debug(f"Writing install script {f.name}")
            f.write("#!/bin/sh\n")
            f.write(f"if command -v {cmd} &> /dev/null; then\n")
            f.write(f"   echo '{cmd} is found';\n")
            f.write( "   exit 0;\n")
            f.write("fi\n")
            f.write(f"PKGNAME=$(pkgfile {cmd})\n")
            f.write(self.install_command("${PKGNAME}"))
            self.scripts[cmd] = Path(f.name)

        fname = self.scripts[cmd]
        artifact = ArtifactTar(f"/bin/bash {fname}", [fname])
        assert artifact.exists()
        return artifact


def test_pkg_manager():
    pm = PackageManger()
    cmd = pm.make_available_command("samtool")
    assert cmd is not None


if __name__ == "__main__":
    test_pkg_manager()
