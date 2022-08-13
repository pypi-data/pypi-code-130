import logging
import time
import petname


class Context:
    applications = []


def generate_name():
    return petname.Generate()


class Application:
    def __init__(self, compose_name, app_name=None):
        if app_name is None:
            app_name = generate_name()
        self.name = app_name
        self.version = "0.0.1"
        self.compose_name = compose_name
        self.start_timestamp = time.time()
        logging.debug(f"Adding application {self.name} to context.")
        Context.applications.append(self)
