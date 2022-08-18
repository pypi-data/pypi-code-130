import pickle


__all__ = [
    "save_env",
    "load_env"
]


def save_env(env, filename, protocol=pickle.HIGHEST_PROTOCOL):
    """Save environment in Python pickle format.

    Parameters
    ----------
    env : environment object
        NeuGym environment object.

    filename : str
       Filename to write.
       Filenames ending in .gz or .bz2 will be compressed.
    protocol : integer
        Pickling protocol to use. Default value: ``pickle.HIGHEST_PROTOCOL``.

    Examples
    --------
    >>> W = GridWorld()
    >>> ng.save_env(W, "test.pkl")

    References
    ----------
    .. [#] https://docs.python.org/3/library/pickle.html

    """
    with open(filename, 'wb') as f:
        pickle.dump(env, f, protocol=protocol)


def load_env(filename):
    """Load environment in Python pickle format.

    Parameters
    ----------
    filename : str
        Filename to read.
        Filenames ending in .gz or .bz2 will be uncompressed.

    Returns
    -------
    W : environment object
        NeuGym environment object.

    Examples
    --------
    >>> W = GridWorld()
    >>> ng.save_env(W, "test.pkl")
    >>> W = ng.load_env("test.pkl")

    References
    ----------
    .. [*] https://docs.python.org/3/library/pickle.html

    """
    with open(filename, 'rb') as f:
        return pickle.load(f)
