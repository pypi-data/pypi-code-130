
from daner import daner


def test_get_key():
    assert daner._get_key('-u') == 'u'
    assert daner._get_key('--user') == 'user'


def test_parse_args():
    assert daner._parse_args(["--name", "milisp"]) == {"name": "milisp"}


def test_set_alias():
    assert daner._set_alias(
        alias={"u": "username"}, obj_in={"u": "milisp"}
    ) == {"username": "milisp"}
