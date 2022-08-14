import os

from tobool import to_bool_strict

use_moto_mock_env_var = "AWSIMPLE_USE_MOTO_MOCK"


def is_mock() -> bool:
    return to_bool_strict(os.environ.get(use_moto_mock_env_var, "0"))
