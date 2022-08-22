import os
from typing import Dict, List

from prompt_toolkit import prompt

PLACEHOLDER_SEPARATOR = "**"


def prompt_env_variables(env_variables: List[str]) -> Dict[str, str]:
    """Uses `prompt_toolkit.prompt` to populate the values of the env_variables

    Args:
        env_variables (List[str]): List of env variables to populate values to

    Returns:
        Dict[str, str]: Dictionary where every keys are env variables with values assigned to them
    """
    env: Dict[str, str] = {}
    for env_variable in env_variables:
        env[env_variable] = prompt(f"{env_variable}=")

    return env


def create_dot_env(env_variables: Dict[str, str], dest_dir: str) -> None:
    """Crate .env file from the dictionary with env variables

    Args:
        env_variables (Dict[str, str]): Dictionary where keys are env variables with values assigned to them
        dest_dir (str): Dir to create the .env file into
    """
    with open(os.path.join(dest_dir, ".env"), "w") as f:
        for k, v in env_variables.items():
            f.write(f"{k}={v}\n")


def _contains_placeholders(line: str, placeholder_keys: List[str]) -> bool:
    """Checks wether a given line contains any of placeholder_keys

    Args:
        line (str): Line to check for placeholders
        placeholder_keys (List[str]): Placeholder keys

    Returns:
        bool: True if the line contains at least one placeholder, else false
    """
    for key in placeholder_keys:
        if _placeholder(key) in line:
            return True

    return False


def _placeholder(key: str, separator=PLACEHOLDER_SEPARATOR) -> str:
    """Converts a key to a template placeholder, according to separator

    Args:
        key (str): Placeholder key
        separator (str, optional): Placeholder separator. Defaults to PLACEHOLDER_SEPARATOR.

    Returns:
        str: Placeholder prefixed and suffixed by the separator, as appears in the .template
    """
    return f"{separator}{key}{separator}"


def populate_template(
    template_path: str, dest_path: str, placeholder_values: Dict[str, str]
) -> None:
    """Populate the given template with values for the placeholder keys and write to destination

    Args:
        template_path (str): Template path
        dest_path (str): Destination path
        placeholder_values (Dict[str, str]): Placeholders with values
    """
    with open(template_path, "r") as template, open(dest_path, "w") as dest:
        for line in template.readlines():
            if PLACEHOLDER_SEPARATOR in line:
                if not _contains_placeholders(line, placeholder_values.keys()):
                    continue

                else:
                    for k, v in placeholder_values.items():
                        if _placeholder(k) in line:
                            dest.write(line.replace(_placeholder(k), v))
            else:
                dest.write(line)
