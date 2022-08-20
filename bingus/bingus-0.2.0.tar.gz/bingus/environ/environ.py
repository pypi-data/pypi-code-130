"""A Module for working with environment variables.

"""
import logging
import os

from .exceptions import *


def require(var_name: str, allow_empty=False) -> str:
    """Get an environment variable and return a sensible error if it doesn't exist or is empy.

    Args:
        var_name: Name of the environment variable to get and require.
        allow_empty: If True, an empty value for the environment variable is accepted.

    Returns:
        str: The value of the environment variable if it exists.

    Raises:
        EmptyEnvironmentVariable: If the environment variable's value is empty
        MissingEnvironmentVariable: If the environment variable is not defined
    """
    logger = logging.getLogger(__name__)
    try:
        var = os.environ[var_name]
        if not allow_empty and var == "":
            message = f"Environment variable {var_name} is empty."
            logger.error(message)
            raise EmptyEnvironmentVariable(message)

    except KeyError:
        message = f"Environment variable {var_name} is not set."
        logger.error(message)
        raise MissingEnvironmentVariable(message)

    return var
