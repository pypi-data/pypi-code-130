#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Atelier AI: Studio for AI Designers                                                 #
# Version    : 0.1.1                                                                               #
# Python     : 3.10.4                                                                              #
# Filename   : /datasource.py                                                                      #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/atelier-ai                                         #
# ------------------------------------------------------------------------------------------------ #
# Created    : Monday August 15th 2022 11:10:14 am                                                 #
# Modified   : Wednesday August 17th 2022 12:09:40 am                                              #
# ------------------------------------------------------------------------------------------------ #
# License    : BSD 3-clause "New" or "Revised" License                                             #
# Copyright  : (c) 2022 John James                                                                 #
# ================================================================================================ #
"""Datasource Module: Creating and Configuring DataSources"""
import os
from abc import ABC, abstractmethod
import shlex
import subprocess
import logging

# ------------------------------------------------------------------------------------------------ #
logging.getLogger(__name__).addHandler(logging.NullHandler())
# ------------------------------------------------------------------------------------------------ #


class Datasource(ABC):
    """Defines the interface for Datasource classes."""

    @abstractmethod
    def extract(self, destination: str) -> None:
        """Extracts data from the Kaggle competition"""


class DatasourceKaggle(Datasource):

    __command_stub = "kaggle competitions download "

    def __init__(self, name: str, competition, filename: str) -> None:
        """Defines a datasource from the Kaggle competition website.

        Args:
            name (str): Unique name for datasource
            competition (str): The name of the Kaggle competition
            filename (str): Name of the file downloaded from Kaggle
        """

        self._name = name
        self._filename = filename
        self._competition = competition

    @property
    def name(self) -> str:
        return self._name

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def competition(self) -> str:
        return self._competition

    def extract(self, destination: str) -> None:
        command = self._format_command(destination)
        os.makedirs(destination, exist_ok=True)
        subprocess.run(shlex.split(command), check=True, text=True, shell=False)

    def _format_command(self, destination: str) -> str:
        return DatasourceKaggle.__command_stub + " -p " + destination + " -c " + self._competition
