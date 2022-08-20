import os


def ensure_dirs_exists(directory_path: str):
    """Function that ensures a directory exists.

    IF the directory doesn't exist, it is created, as well as any parent directory.

    Args:
        directory_path (str): Path of the directory to ensure.

    Returns:
        str: :param:`directory_path`

    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    return directory_path
