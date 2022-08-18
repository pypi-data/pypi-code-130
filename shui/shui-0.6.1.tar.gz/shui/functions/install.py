"""Functions for installing a particular version from a local tarball"""
import tarfile
import pathlib3x as pathlib
from shui.classes import FileInfo


def extract_tarball(tarball: FileInfo, install_dir: pathlib.Path) -> pathlib.Path:
    """Extract tarball to a local path"""
    if not tarball.path.is_file():
        raise IOError(f"<info>{tarball.path}</info> is not a file!")
    try:
        with tarfile.open(tarball.path, "r:gz") as f_tarball:
            extraction_dir = [
                obj.name
                for obj in f_tarball.getmembers()
                if obj.isdir() and "/" not in obj.name
            ][0]
            f_tarball.extractall(install_dir)
    except tarfile.ReadError as exc:
        raise IOError(f"<info>{tarball.path}</info> is not a valid tarball!") from exc
    return install_dir / extraction_dir
