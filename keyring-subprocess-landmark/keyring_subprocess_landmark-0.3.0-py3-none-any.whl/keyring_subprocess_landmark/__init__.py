__version__ = "0.3.0"


class KeyringEntryPointNotFoundError(Exception):
    pass


def keyring_subprocess():
    import sys

    if sys.version_info > (3, 10):
        from importlib import metadata
    else:
        import importlib_metadata as metadata

    console_scripts = metadata.entry_points(group="console_scripts")

    if "keyring" not in console_scripts.names:
        raise KeyringEntryPointNotFoundError(
            "No 'keyring' entry point found in the 'console_scripts' group, is keyring installed?"
        )

    console_script = console_scripts["keyring"].load()

    backends = metadata.entry_points(group="keyring.backends")

    if "keyring-subprocess" not in backends.names:
        raise KeyringEntryPointNotFoundError(
            "No 'keyring-subprocess' entry point found in the 'keyring.backends' group, "
            "is keyring-subprocess installed?"
        )

    backend = backends["keyring-subprocess"].load()

    import keyring

    keyring.set_keyring(backend())

    return console_script()
