import logging


def install_application(template="template.yaml", values=None):
    if values is None:
        values = ["values.yaml"]
    logging.info(f"Values: {values}")