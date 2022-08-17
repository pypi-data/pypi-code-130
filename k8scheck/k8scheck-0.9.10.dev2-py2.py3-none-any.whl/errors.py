class KubetestError(Exception):
    """Base class for all k8scheck exceptions."""


class SetupError(KubetestError):
    """Failed to perform test setup actions."""
