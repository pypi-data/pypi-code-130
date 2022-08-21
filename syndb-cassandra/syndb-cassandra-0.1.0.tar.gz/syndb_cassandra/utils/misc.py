import subprocess
from collections.abc import Iterable
from pathlib import Path

from pydantic import DirectoryPath, typing


def materialized_view_name_from_table_name_and_partition_key(
    table_name: str, new_partition_key: str | typing.Iterable
) -> str:
    if isinstance(new_partition_key, Iterable):
        new_partition_key = "_".join(new_partition_key)

    return f"{table_name}_{new_partition_key}"


def get_class_names(classes: Iterable):
    return tuple(model.__table_name__ for model in classes)


def get_git_repo_root() -> DirectoryPath:
    return Path(
        subprocess.Popen(
            ["git", "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            cwd=str(Path(__file__).absolute().parent),
        )
        .communicate()[0]
        .rstrip()
        .decode("utf-8")
    )


def auto_dir_for_testing() -> DirectoryPath:
    result = get_git_repo_root() / "auto"
    result.mkdir(exist_ok=True)
    return result
