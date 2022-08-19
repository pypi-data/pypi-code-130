#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# standard python imports

""" Application Configuration """
import os
import sys
from collections.abc import MutableMapping
from pathlib import Path
from subprocess import PIPE, STDOUT, Popen

import yaml

from app.logz import create_logger


class Application(MutableMapping):
    """
    Regscale CLI configuration class
    """

    def __init__(self):
        """constructor"""

        template = {
            "domain": "https://mycompany.regscale.com/",
            "wizAccessToken": "<createdProgrammatically>",
            "wizClientId": "<myclientidgoeshere>",
            "wizClientSecret": "<mysecretgoeshere>",
            "wizScope": "<filled out programmatically after authenticating to Wiz>",
            "wizUrl": "<my Wiz URL goes here>",
            "wizAuthUrl": "https://auth.wiz.io/oauth/token",
            "wizExcludes": "My things to exclude here",
            "adAuthUrl": "https://login.microsoftonline.com/",
            "adGraphUrl": "https://graph.microsoft.com/.default",
            "adAccessToken": "Bearer <my token>",
            "adClientId": "<myclientidgoeshere>",
            "adSecret": "<mysecretgoeshere>",
            "adTenantId": "<mytenantidgoeshere>",
            "jiraUrl": "<myJiraUrl>",
            "jiraUserName": "<jiraUserName>",
            "jiraApiToken": "<jiraAPIToken>",
            "snowUrl": "<mySnowUrl>",
            "snowUserName": "<snowUserName>",
            "snowPassword": "<snowPassword>",
            "userId": "enter user id here",
            "oscal_location": "/opt/OSCAL",
            "saxon_path": "/opt/saxon-he-11.4.jar",
        }
        logger = create_logger()
        self.template = template
        self.templated = False
        self.logger = logger
        config = self._gen_config()
        self.config = config
        try:
            if not Path(self.config["oscal_location"]).exists():
                logger.warning(
                    "OSCAL folder path does not exist, please check init.yaml"
                )
        except TypeError as ex:
            logger.error(ex)

    def __getitem__(self, key):
        """Get an item."""
        return self.config.__getitem__(self, key)

    def __setitem__(self, key, value):
        """Set an item."""

        value = int(value)
        if not 1 <= value <= 10:
            raise ValueError(f"{value} not in range [1,10]")
        self.config.__setitem__(self, key, value)

    def __delitem__(self, key):
        """Delete an item."""

        self.config.__delitem__(self, key)

    def __iter__(self):
        """return iterator"""
        return self.config.__iter__(self)

    def __len__(self):
        """get the length of the config."""

        return self.config.__len__(self)

    def __contains__(self, x: str):
        """Check config if it contains string."""

        return self.config.__contains__(self, x)

    def _gen_config(self) -> dict:
        """Generate the Application config from file or environment

        Returns:
            dict: configuration
        """
        config = None
        try:
            env = self._get_env()
            file_config = self._get_conf() if self._get_conf() else {}
            self.logger.debug("file_config: %s", file_config)
            # Merge
            if self.templated is False:
                config = {**file_config, **env}
            else:
                config = {**env, **file_config}

        except TypeError as ex:
            self.logger.error("TypeError: No configuration loaded!!! Exiting.. %s", ex)
            # sys.exit()
        if config is not None:
            self.save_config(config)

        # Return config
        return config

    def _get_env(self) -> dict:
        """return dict of regscale keys from system"""
        all_keys = self.template.keys()
        sys_keys = [key for key in os.environ if key in all_keys]
        #  Update Template
        dat = None
        try:
            dat = self.template.copy()
            for k in sys_keys:
                dat[k] = os.environ[k]
        except KeyError as ex:
            self.logger.error("Key Error!!: %s", ex)
        self.logger.debug("dat: %s", dat)
        if dat == self.template:
            # Is the generated data the same as the template?
            self.templated = True
        return dat

    def _get_conf(self) -> dict:
        """Get configuration from init.yaml if exists"""
        config = None
        fname = "init.yaml"
        # load the config from YAML
        try:
            with open(fname, encoding="utf-8") as stream:
                config = yaml.safe_load(stream)
        except FileNotFoundError as ex:
            self.logger.error(ex)
        self.logger.debug("_get_conf: %s, %s", config, type(config))
        return config

    @classmethod
    def save_config(cls, conf: dict):
        """Save Configuration to init.yaml

        Args:
            conf (dict): Dict configuration
        """
        try:
            with open("init.yaml", "w", encoding="utf-8") as file:
                yaml.dump(conf, file)
        except OSError:
            print("Could not dump config to init.yaml")

    @staticmethod
    def load_config() -> dict:
        """Load Configuration

        Returns:
            dict: Dict of config
        """
        with open("init.yaml", "r", encoding="utf-8") as stream:
            return yaml.safe_load(stream)

    @staticmethod
    def get_java() -> str:
        """
        Get Java Version from system
        Returns:
            str: Java Version
        """
        command = "java --version"
        java8_command = "java -version"
        with (Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)) as p_cmd, (
            Popen(java8_command, shell=True, stdout=PIPE, stderr=STDOUT)
        ) as alt_cmd:
            out = iter(p_cmd.stdout.readline, b"")
            result = list(out)[0].decode("utf-8").rstrip("\n")
            if result == "Unrecognized option: --version":
                out = iter(alt_cmd.stdout.readline, b"")
                result = list(out)[0].decode("utf-8").rstrip("\n")
            return result
