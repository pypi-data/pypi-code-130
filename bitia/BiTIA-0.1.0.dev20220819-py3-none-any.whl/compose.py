"""Generate compose file."""

__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import typing as T
import collections
import itertools
import logging
from pathlib import Path

import yaml
from jinja2 import Template

import bitia.common
import bitia.common.path

# Thanks https://stackoverflow.com/a/19323121/1805129
from yaml.representer import Representer

yaml.add_representer(collections.defaultdict, Representer.represent_dict)


DEFAULT_DOCKER_TEMPLATE = Template(
    """
FROM subcom/bio.copr:bioarchlinux
RUN python -m ensurepip
# RUN python -m pip install bitia --pre
RUN python -m pip install git+https://gitlab.subcom.tech/SubconsciousCompute/bitia 
{{ run_steps }}
"""
)


def _docker_filepath(user_input, *args) -> Path:
    return bitia.common.path.get_workdir(user_input).joinpath(*args)


class ComposeFile(object):
    """Generates docker-compose file as well as Dockerfile to run this pipeline."""

    def __init__(self, user_input):
        assert user_input is not None
        self.user_input = user_input
        self.dockerfile_path = _docker_filepath(self.user_input, ".bitia", "Dockerfile")
        self.composefile_path = _docker_filepath(self.user_input, "docker-compose.yaml")
        self.compose = collections.defaultdict(dict)
        self.dockerfile_params = collections.defaultdict(str)
        self.init()

    def init(self):
        self.compose["version"] = "3.0"
        self.compose["services"]["default"] = self.default_service()
        self.compose["volumes"] = self.init_volumes()

    def add_job(self, user_input):
        """Setup docker-compose environment for user input"""
        assert self.user_input is None, "job is already set for this compose file"
        self.user_input = user_input

    def default_service(self):
        return dict(
            # container_name=self.user_input,
            build=dict(context=".", dockerfile=str(self.dockerfile_path)),
            volumes=[".:/app", "/tmp:/tmp"],
            # ports=["3141:3141"],
        )

    def dockerfile_str(self):
        return DEFAULT_DOCKER_TEMPLATE.render(self.dockerfile_params)

    def init_volumes(self):
        return {}

    def __repr__(self):
        return yaml.dump(self.compose, sort_keys=False)

    def finalize(self):
        logging.info("Finalizing...")
        self.dockerfile_path.parent.mkdir(parents=True, exist_ok=True)
        with self.dockerfile_path.open("w") as f:
            logging.info(f"Writing Dockerfile {f.name}")
            f.write(self.dump_dockerfile())
        with self.composefile_path.open("w") as f:
            logging.info(f"Writing {f.name}")
            f.write(self.__repr__())

    def _setup_docker_file(self, executables: T.List[str]):
        logging.info(f"Making sure that {exec} exists")
        self.dockerfile_params[
            "run_steps"
        ] = f"RUN bitia tools ensures {' '.join(executables)}"

    def _user_input_to_command(self) -> str:
        if Path(self.user_input).is_file():
            return f"bash {self.user_input}"
        elif Path(self.user_input).is_dir():
            return f"bash {self.user_input}"
        else:
            return f"bash -c '{self.user_input}'"

    def _setup_compose_file(self):
        self.compose["services"]["default"]["command"] = self._user_input_to_command()

    def dump_dockerfile(self):
        return self.dockerfile_str()

    def populate_docker_files(self):
        """TODO: Docstring for populate_docker_files.

        :returns: TODO

        """
        if Path(self.user_input).is_file():
            raise NotImplementedError(
                f"Setup docker compose for file {self.user_input}"
            )
        elif Path(self.user_input).is_dir():
            raise NotImplementedError(f"Setup docker compose for dir {self.user_input}")
        else:
            # TODO: Extract required installables from the user_input and create
            # docker file.
            cmds = [self.user_input.split()[0]]
            self._setup_docker_file(cmds)
            # Setup docker-compose file to run the pipeline.
            self._setup_compose_file()

    def run(self, check: bool = False):
        self.populate_docker_files()
        self.finalize()
        cwd = self.composefile_path.resolve().parent
        assert cwd.exists()
        return bitia.common.run_command(
            "docker-compose up --build --no-color", cwd=cwd, check=check
        )
