import subprocess
from functools import cached_property
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, DirectoryPath, validate_arguments
from ruamel.yaml import YAML

yaml = YAML()


class SyndbCliConfig(BaseModel):
    manual_project_root_path: Optional[DirectoryPath]

    class Config:
        keep_untouched = (cached_property,)

    @cached_property
    def config(self) -> dict:
        return yaml.load(self.project_root_path / "syndb_config.yaml")

    @cached_property
    def project_root_path(self) -> DirectoryPath:
        return self.manual_project_root_path or Path(
            subprocess.Popen(["git", "rev-parse", "--show-superproject-working-tree"], stdout=subprocess.PIPE)
            .communicate()[0]
            .rstrip()
            .decode("utf-8")
        )

    @cached_property
    def syndb_client_repository_path(self) -> DirectoryPath:
        return self._combine_with_project_root(self.config["syndb-client_path"])

    @cached_property
    def syndb_client_path(self) -> DirectoryPath:
        return self.syndb_client_repository_path / "client"

    @cached_property
    def syndb_fastapi_repository_path(self) -> DirectoryPath:
        return self._combine_with_project_root(self.config["syndb-fastapi_path"])

    @cached_property
    def syndb_fastapi_path(self) -> DirectoryPath:
        return self.syndb_fastapi_repository_path / "syndb_backend"

    @cached_property
    def syndb_fastapi_dist_path(self) -> DirectoryPath:
        return self.syndb_fastapi_repository_path / "dist"

    @cached_property
    def syndb_cassandra_path(self) -> DirectoryPath:
        return self._combine_with_project_root(self.config["syndb-cassandra_path"])

    @property
    def openapi_spec_client_path(self) -> Path:
        return self.syndb_client_repository_path / f"{self.config['openapi_spec_file-stem']}.yaml"

    @property
    def openapi_gen_path(self) -> Path:
        return self.syndb_client_repository_path / "fastapi"

    def _combine_with_project_root(self, sub_path: Path | str) -> Path:
        return self.project_root_path / sub_path
