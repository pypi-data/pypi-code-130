from __future__ import annotations

import sys
from pathlib import Path
from subprocess import check_call

import pytest
from pytest_mock import MockerFixture

from bump_deps_index import Options, main


def test_main(capfd: pytest.CaptureFixture[str]) -> None:
    check_call([sys.executable, "-m", "bump_deps_index", "-h"])
    out, err = capfd.readouterr()
    assert out
    assert not err


def test_script(capfd: pytest.CaptureFixture[str]) -> None:
    check_call([Path(sys.executable).parent / "bump-deps-index", "-h"])
    out, err = capfd.readouterr()
    assert out
    assert not err


def test_main_py(mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("PIP_INDEX_URL", raising=False)
    monkeypatch.delenv("NPM_REGISTRY_CONFIG", raising=False)
    run = mocker.patch("bump_deps_index.run")
    main(["A"])
    opt = Options(
        index_url="https://pypi.org/simple",
        npm_registry="https://registry.npmjs.org",
        pkgs=["A"],
        filenames=[],
    )
    run.assert_called_once_with(opt)
