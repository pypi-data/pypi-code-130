"""
Copyright (C) 2022 Subconscious Compute 'All rights reserved.'
"""

import typing as T
import logging

import bitia.common
import bitia.compose

import typer

from rich import print as rprint

app = typer.Typer()


def _url_validate(url):
    """URL validation"""
    from urllib.parse import urlparse

    o = urlparse(url)
    assert o is not None
    assert o.scheme in ["http", "https"]


def submit_job(
    user_input: str,
    *,
    server: T.Optional[str] = None,
    executor: bitia.common.Executor = bitia.common.Executor.podman,
    interactive: bool = False,
):
    r"""runs the passed command or file inside a docker container and returns the output

    Parameteres
    -----------
    user_input : str
        It could be a command, a directory or a file.
    server : str, optional
        Gets the server address from the user.
    executor: str, optional
        'bash', 'docker', 'podman'
    interactive: bool, default `False'
        When `True`, run container in interactive mode.

    Returns
    -------
    None

    See Also
    --------
    bitia.daemon.daemon

    """
    if server is None:
        server = bitia.config.server()
    if executor is None:
        executor = bitia.config.executor()
    _url_validate(server), "given server url is invalid, please enter a valid url"
    # Jobs are run on the server. It is here because we are testing it right
    # now.
    compose = bitia.compose.ComposeFile(user_input)
    for line in compose.run():
        print(line)
