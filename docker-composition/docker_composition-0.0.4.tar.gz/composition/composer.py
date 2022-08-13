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

    def install(self, template="template.yaml", values=["values.yaml"]):
        """
        Install a docker-compose application with
        :param template: str
            The name of the template file to install (defaults to template.yaml)
        :param values: list[str]
            A list of values files to generate templates from
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
    root = logging.getLogger()
    hdlr = root.handlers[0]
    fmt = logging.Formatter('%(message)s')
    hdlr.setFormatter(fmt)
    fire.core.Display = lambda lines, out: print(*lines, file=out)
    fire.Fire(CommandLineInterface)


if __name__ == "__main__":
    entrypoint()
