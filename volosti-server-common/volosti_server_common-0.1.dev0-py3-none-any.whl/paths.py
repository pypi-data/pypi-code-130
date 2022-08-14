from pathlib import Path


def _get_package_path() -> Path:
    return Path(__file__).resolve().parent


def get_static_path() -> Path:
    return _get_package_path() / 'static'


def get_templates_path() -> Path:
    return _get_package_path() / 'templates'
