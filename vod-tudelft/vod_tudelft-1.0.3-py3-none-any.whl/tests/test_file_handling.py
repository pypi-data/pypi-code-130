import os
import tempfile

import pytest

from vod import get_frame_list


def test_get_frame_list_exception():
    with pytest.raises(ValueError):
        get_frame_list("wrong_location")


def test_get_frame_list_correct():
    fd = tempfile.NamedTemporaryFile()
    try:
        with open(fd.name, 'w') as tmp:
            # do stuff with temp file
            tmp.write('1')
            tmp.write('\n')
            tmp.write('2')
        test = get_frame_list(fd.name)
        expected_value = ['1', '2']
        assert test == expected_value

    finally:
        os.remove(fd.name)


