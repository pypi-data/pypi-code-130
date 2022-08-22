from sugarloaf_utilities.terraform import should_init
import pytest

@pytest.mark.parametrize("message,expected", [
    # Sometimes errors are broken per line
    ('This module is not yet installed. Run\n"terraform init" to install all\nmodules required by this configuration.', True)
])
def test_parse_init_error(message, expected):
    assert should_init(message) == expected
