"""Test locale gen file."""

import os
from pathlib import Path
from spec import fn


def test_locale_dot_gen_file(mock_pyproject_path):
    """Test generate locale.gen file."""

    gen_file = fn.locale_dot_gen()

    assert gen_file == Path(fn.app_dir() / 'locale.gen')
    assert not gen_file.exists()

    try:
        fn.create_locale_dot_gen()
        assert gen_file.exists()
    except Exception as _exc:
        raise
    finally:
        os.remove(gen_file.as_posix())
        assert not gen_file.exists()
