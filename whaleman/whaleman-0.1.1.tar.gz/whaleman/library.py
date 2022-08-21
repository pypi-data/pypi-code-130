from docker import APIClient
import configparser
import os
import click
from os.path import exists as file_exists
from .logs import ColorLogger
import logging

logging.setLoggerClass(ColorLogger)

logger = logging.getLogger(__name__)


class Versioner:
    def __init__(self, version: str) -> None:
        self.major, self.minor, self.micro = version.split(".")
        self.major = int(self.major)
        self.minor = int(self.minor)
        self.micro = int(self.micro)

    def patch_micro(self):
        self.micro += 1

    def patch_minor(self):
        self.minor += 1
        self.micro = 0

    def patch_major(self):
        self.major += 1
        self.minor = 0
        self.micro = 0

    @property
    def version(self) -> str:
        return "{}.{}.{}".format(self.major, self.minor, self.micro)


class BaseRun:
    client = APIClient(base_url="unix://var/run/docker.sock")
    config = configparser.ConfigParser()

    def __init__(self, args) -> None:
        logger.setLevel(args.level)
        self.args = args
        self.is_ini_extension()

    def is_ini_extension(self):
        if not self.args.filename.endswith(".ini"):
            raise ValueError("file extension must be .ini")


class DockerRun(BaseRun):
    def __init__(self, args) -> None:
        super().__init__(args)
        if not file_exists(self.args.filename):
            raise NotImplementedError(f"{self.args.filename} not found")
        self.config.read(self.args.filename)
        self.is_login = self.config.getboolean("registry", "login")
        self.registry = self.config.get("registry", "name")
        self.tag = self.config.get("image", "tag")
        self.version = Versioner(self.tag)
        logger.debug("prev version: {}".format(self.version.version))
        getattr(self.version, f"patch_{args.version}")()
        logger.debug("next version: {}".format(self.version.version))
        self.image = self.config.get("image", "name")
        logger.debug("image name: {}".format(self.image))
        self.image_tag = "{}/{}:{}".format(
            self.registry, self.image, self.version.version
        )
        logger.debug("image tag: {}".format(self.image_tag))
        self.image_tag_latest = "{}/{}:{}".format(self.registry, self.image, "latest")
        logger.debug("image tag latest: {}".format(self.image_tag_latest))

    def login(self):
        logger.debug("Start login")
        try:
            self.client.login(
                username=self.config.get(
                    "registry", "docker_username", fallback=None, vars=os.environ
                ),
                password=self.config.get(
                    "registry", "docker_password", fallback=None, vars=os.environ
                ),
                registry=self.registry,
            )
            logger.info("Logged in to {}".format(self.registry))
        except Exception as e:
            logger.error("Failed to login to {}".format(self.registry))
            logger.error(e)

    def build(self, tag) -> None:
        logger.debug("Start build")
        logger.debug("building image with tag: {}".format(tag))
        result = self.client.build(
            path=".", tag=tag, decode=True, dockerfile=self.args.dockerfile
        )
        for chunk in result:
            if "stream" in chunk:
                for line in chunk["stream"].splitlines():
                    logger.info(line)

    def push(self, repo_tag) -> None:
        if self.is_login:
            self.login()
        result = self.client.push(repo_tag, stream=True, decode=True)
        for line in result:
            logger.info(
                line.get("status", ""), line.get("progress", ""), line.get("id", "")
            )

    def __call__(self) -> None:
        self.build(self.image_tag)
        logger.debug("image with tag: {}".format(self.image_tag))
        self.client.tag(self.image_tag, self.image_tag_latest)
        logger.debug("retag image with latest tag: {}".format(self.image_tag_latest))
        if self.args.push:
            self.push(self.image_tag)
            self.push(self.image_tag_latest)
        self.config.set("image", "tag", self.version.version)
        with open(self.args.filename, "w") as configfile:
            self.config.write(configfile)


class DockerRunCreateConfig(BaseRun):
    @staticmethod
    def check_is_valid_version(version: str) -> bool:
        # version format should be like "1.0.0"
        if not version.count(".") == 2:
            raise ValueError("version format should be like 1.0.0")
        list_ver: list = version.split(".")
        try:
            [int(i) for i in list_ver]
        except ValueError:
            raise ValueError("version format only support int")
        return version

    def __call__(self) -> None:
        self.config.add_section("image")
        self.config.add_section("registry")
        image_name = click.prompt(click.style("input image name", fg="green"), type=str)
        tag = click.prompt(
            click.style("input initial tag", fg="green"),
            type=str,
            value_proc=DockerRunCreateConfig.check_is_valid_version,
        )
        registry_uri = click.prompt(
            click.style(
                "input registry uri, leave blank to set default as ->", fg="green"
            ),
            type=str,
            default="index.docker.io",
            show_default=True,
        )
        need_login = click.confirm(
            click.style("need login?", fg="green"), default=False
        )
        if need_login:
            click.echo(
                click.style(
                    "Leave it blank if you want use environment variables credentials, \n export DOCKER_USERNAME=xxx \n export DOCKER_PASSWORD=xxx",
                    fg="yellow",
                )
            )
            username = click.prompt(
                click.style("input username", fg="green"), default=""
            )
            password = click.prompt(
                click.style("input password", fg="green"), default=""
            )
            if username != "":
                self.config.set("registry", "docker_username", username)
            if password != "":
                self.config.set("registry", "docker_password", password)
        self.config.set("registry", "login", str(need_login))
        self.config.set("registry", "name", registry_uri)
        self.config.set("image", "name", image_name)
        self.config.set("image", "tag", tag)
        with open(self.args.filename, "w") as configfile:
            self.config.write(configfile)
