import shutil
import subprocess
from pathlib import Path
from typing import Optional

import click
import pkg_resources
from click import option
from pydantic import FilePath, validate_arguments
from syndb_cassandra import PROJECT_NAME
from syndb_cassandra.client_app_data import client_app_data
from syndb_cassandra.initialize import create_syndb_tables
from syndb_cassandra.settings import (
    cassandra_settings_getter,
    outside_production_settings,
)


@click.group()
def sycass():
    pass


@sycass.command()
@option(
    "-s",
    "--settings",
    "settings_json",
    type=str,
    help="Path to JSON storing settings key-value pairs",
)
@validate_arguments
def tables(settings_json: Optional[FilePath] = None):
    create_syndb_tables(settings=_cli_setting_getter(settings_json))


@sycass.command()
@option(
    "-s",
    "--settings",
    "settings_json",
    type=str,
    help="Path to JSON storing settings key-value pairs",
)
@validate_arguments
def outside_tables(settings_json: Optional[FilePath] = None):
    create_syndb_tables(settings=outside_production_settings())


@sycass.command()
@option(
    "-o",
    "--out",
    "out_file_path",
    type=str,
    help="Path to JSON file for storing results",
)
@validate_arguments
def app_data(out_file_path: Optional[Path] = None) -> None:
    client_app_data(out_file_path, dry_run=not out_file_path)
    if not out_file_path:
        print("Save data by providing file path in the -o option")


@sycass.command()
def dockerize():
    root = _repository_root()
    dist_path = root / "dist"

    base_image_name = f"caniko/{PROJECT_NAME}:"

    version = pkg_resources.get_distribution("syndb_cassandra").version
    version_image_name = f"{base_image_name}{version}"

    latest_image_name = f"{base_image_name}latest"

    if dist_path.exists():
        shutil.rmtree(dist_path)

    subprocess.check_call(
        ["poetry", "build", "-f", "wheel"],
        cwd=root,
    )
    subprocess.check_call(
        ["docker", "build", "-t", version_image_name, "-t", latest_image_name, root],
        cwd=root,
    )
    subprocess.check_call(["docker", "push", version_image_name])
    subprocess.check_call(["docker", "push", latest_image_name])


def _cli_setting_getter(settings_json: FilePath | None = None):
    settings_class = cassandra_settings_getter()
    return (
        settings_class.from_json(settings_json) if settings_json else settings_class()
    )


def _repository_root():
    return Path(
        subprocess.Popen(
            ["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE
        )
        .communicate()[0]
        .rstrip()
        .decode("utf-8")
    )
