import logging

def get_logger(name):
    """
    Creates logger object using name. The returned logger object logs to the standard error stream and formats
    the messages.

    Parameters
    ----------
        name: The name that gets passed to the logger.getLogger function.
    Returns
    -------
        A logger instance with the given name.
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    stderr_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)
    return logger