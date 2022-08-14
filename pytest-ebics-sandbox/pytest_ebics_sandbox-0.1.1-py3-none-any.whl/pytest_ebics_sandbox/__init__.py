import time
from collections import namedtuple
from contextlib import suppress
from urllib.parse import urljoin
from uuid import uuid4

import docker
import pytest
import requests
from docker.errors import NotFound
from requests.exceptions import ConnectionError
from urllib3.exceptions import ProtocolError

SANDBOX_IMAGE = "ghcr.io/henryk/libeufin/sandbox:latest"

Credentials = namedtuple("Credentials", ("username", "password"))


class EbicsSandbox:
    def __init__(self):
        self.admin_credentials = Credentials("admin", "hunter2")
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
                json={"hostID": self.ebics_host, "ebicsVersion": "3.0"},
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
        response = self._session.get(self.base_url)
        return response.status_code == 200 and "this is the Sandbox" in response.text

    def rotate_keys(self):
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
        self._container = self.docker_client.containers.run(
            SANDBOX_IMAGE,
            detach=True,
            auto_remove=True,
            environment={
                "LIBEUFIN_SANDBOX_ADMIN_PASSWORD": self.admin_credentials.password,
                "LIBEUFIN_SANDBOX_DB_CONNECTION": "jdbc:sqlite:/data/libeufindb.sqlite3",
            },
            tmpfs={"/data": ""},
            ports={"5002/tcp": None},
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
def ebics_sandbox() -> EbicsSandbox:
    with EbicsSandbox() as sandbox:
        yield sandbox
