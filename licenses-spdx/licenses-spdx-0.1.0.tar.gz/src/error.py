import warnings

class LicenseOriginURLMissingError(Exception):
    def __init__(self, values) -> None:
        super().__init__(
            f'License "{values.full_name}" missing any URL pointing to its origin'
        )

class LicenseNotFoundError(ValueError):
    def __init__(self, name) -> None:
        super().__init__(
            f'License with spdx_id or full_name "{name}" is not available'
        )
        
def MultipleLicensesWarning(name):
    warnings.warn("Multiple licenses with spdx_id or full_name {} are available, returning a List".format(name), RuntimeWarning)