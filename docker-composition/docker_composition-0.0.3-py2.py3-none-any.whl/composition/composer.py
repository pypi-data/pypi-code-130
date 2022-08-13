import logging
import os

import fire


class CommandLineInterface:
    """
    A docker-compose package manager.

    install - Installs a given template
    list - Lists installed applications
    log_level - Sets the log level for the application
    """

    def install(self, template="template.yaml"):
        """

        :param template: str
            The name of the template file to install (defaults to template.yaml)
        :return:
        """
        logging.debug(f"Installing template {template}")
        logging.info(f"Hello, {os.getcwd()}, template {template}")

    def list(self):
        logging.debug("Listing...")

    def log_level(self, level=None):
        if level is None:
            logging.info(f"Current log level is {logging.root.level}")
        logging.debug(f"Setting log level to {level}")
        logging.root.setLevel(level)


def entrypoint():
    logging.basicConfig(level=logging.INFO)
    fire.core.Display = lambda lines, out: print(*lines, file=out)
    fire.Fire(CommandLineInterface)


if __name__ == "__main__":
    entrypoint()
