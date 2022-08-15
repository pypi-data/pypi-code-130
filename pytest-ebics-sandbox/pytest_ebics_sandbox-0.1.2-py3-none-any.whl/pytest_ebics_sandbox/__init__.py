import time
from collections import namedtuple
from contextlib import suppress
from copy import deepcopy
from typing import Optional
from urllib.parse import urljoin
from uuid import uuid4

import docker
import pytest
import requests
from docker.errors import NotFound
from requests.exceptions import ConnectionError
from urllib3.exceptions import ProtocolError

DEFAULT_SANDBOX_DOCKER_CONFIGURATION = {
    "auto_remove": True,
    "tmpfs": {"/data": ""},
    "ports": {"5002/tcp": None},
    "environment": {
        "LIBEUFIN_SANDBOX_DB_CONNECTION": "jdbc:sqlite:/data/libeufindb.sqlite3",
    },
}
DEFAULT_EBICS_SANDBOX_SETTINGS = {
    "ebics_version": "3.0",
    "sandbox_image": "ghcr.io/henryk/libeufin/sandbox:latest",
    "admin_password": "hunter2",
}


Credentials = namedtuple("Credentials", ("username", "password"))


class EbicsSandbox:
    def __init__(
        self,
        /,
        sandbox_settings: Optional[dict] = None,
        docker_configuration: Optional[dict] = None,
    ):
        self._docker_configuration = (
            docker_configuration
            if docker_configuration is not None
            else DEFAULT_SANDBOX_DOCKER_CONFIGURATION
        )
        self._sandbox_settings = (
            sandbox_settings
            if sandbox_settings is not None
            else DEFAULT_EBICS_SANDBOX_SETTINGS
        )

        self.admin_credentials = Credentials(
            "admin", self._sandbox_settings["admin_password"]
        )
        self.ebics_host = str(uuid4())

        self._docker_client = None
        self._container = None
        self._base_url = None
        self._session = None

    def _ensure_started(self):
        if not self._container:
            self.start_container()

            for i in range(15):
                with suppress(ProtocolError, ConnectionError):
                    if self.ping():
                        break
                time.sleep(0.5)

            response = self._session.post(
                urljoin(self.base_url, "/admin/ebics/hosts"),
                json={
                    "hostID": self.ebics_host,
                    "ebicsVersion": self._sandbox_settings["ebics_version"],
                },
            )
            response.raise_for_status()

    @property
    def base_url(self):
        self._ensure_started()
        return self._base_url

    @property
    def ebics_url(self):
        return urljoin(self.base_url, "/ebicsweb")

    @property
    def docker_client(self):
        if not self._docker_client:
            self._docker_client = docker.from_env()
        return self._docker_client

    def ping(self):
        self._ensure_started()
        response = self._session.get(self.base_url)
        return response.status_code == 200 and "this is the Sandbox" in response.text

    def rotate_keys(self):
        self._ensure_started()
        response = self._session.post(
            urljoin(self.base_url, f"/admin/ebics/hosts/{self.ebics_host}/rotate-keys")
        )
        return response.status_code == 200

    def cleanup(self):
        if self._container:
            self.stop_container()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def start_container(self):
        args = dict(
            self._docker_configuration,
            detach=True,
        )
        args["environment"] = args.get("environment", {}) | {
            "LIBEUFIN_SANDBOX_ADMIN_PASSWORD": self.admin_credentials.password,
        }
        self._container = self.docker_client.containers.run(
            self._sandbox_settings["sandbox_image"], **args
        )

        while self._container.status == "created":
            time.sleep(0.1)
            self._container.reload()

        port = self._container.attrs["NetworkSettings"]["Ports"]["5002/tcp"][0][
            "HostPort"
        ]

        self._base_url = f"http://127.0.0.1:{port}"
        self._session = requests.Session()
        self._session.auth = self.admin_credentials

    def stop_container(self):
        if self._container:
            with suppress(NotFound):
                self._container.stop()
            self._container = None

    def new_subscriber(self) -> "EbicsSandboxSubscriber":
        self._ensure_started()
        retval = EbicsSandboxSubscriber(self)
        response = self._session.post(
            urljoin(self.base_url, f"admin/ebics/subscribers"),
            json={
                "hostID": retval.host_id,
                "userID": retval.user_id,
                "partnerID": retval.partner_id,
            },
        )
        response.raise_for_status()
        return retval


class EbicsSandboxSubscriber:
    def __init__(self, sandbox: EbicsSandbox):
        self.sandbox = sandbox
        self.host_id = sandbox.ebics_host
        self.user_id = "u-" + str(uuid4())
        self.partner_id = "p-" + str(uuid4())


@pytest.fixture(scope="session")
def ebics_sandbox_docker_configuration():
    return deepcopy(DEFAULT_SANDBOX_DOCKER_CONFIGURATION)


@pytest.fixture(scope="session")
def ebics_sandbox_settings():
    return deepcopy(DEFAULT_EBICS_SANDBOX_SETTINGS)


@pytest.fixture(scope="session")
def ebics_sandbox(
    ebics_sandbox_settings, ebics_sandbox_docker_configuration
) -> EbicsSandbox:
    with EbicsSandbox(
        sandbox_settings=ebics_sandbox_settings,
        docker_configuration=ebics_sandbox_docker_configuration,
    ) as sandbox:
        yield sandbox
