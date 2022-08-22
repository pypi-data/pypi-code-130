from pathlib import Path


def foo() -> str:
    return Path(Path(__file__).parent.resolve(), "foo.foo").read_text().strip()


def bar() -> None:
    print(foo())
