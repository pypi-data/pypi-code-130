# external
from enum import Enum
from typing import Any, Callable, Container, List, Literal, Type, Union
from pytest import raises
# local
from refcontainer import Ref, ReadOnlyError


def test_empty():
    with raises(TypeError):
        ref = Ref()


def test_starting_value():
    ref = Ref('hello')
    assert ref.current == 'hello'


def test_overwrite():
    ref = Ref('hello')
    ref.current = 'world'
    assert ref.current == 'world'


def test_delete():
    ref = Ref('hello')
    del ref.current
    with raises(AttributeError):
        _ = ref.current
    ref.current = 'world'
    assert ref.current == 'world'


def test_engrave():
    ref = Ref('')
    ref.engrave('hello')
    with raises(ReadOnlyError):
        ref.current = 'world'
    with raises(ReadOnlyError):
        del ref.current
    with raises(ReadOnlyError):
        ref.engrave('world')
    assert ref.current == 'hello'


def test_readonly():
    ref = Ref.readonly('hello')
    with raises(ReadOnlyError):
        del ref.current
    assert ref.current == 'hello'


def test_type_change():
    ref = Ref('hello')
    with raises(TypeError):
        ref.current = 0


def test_tagged_union():
    ref = Ref[Union[str, int]]('hello')
    # ref = Ref[str | int]('hello')
    assert ref.current == 'hello'
    ref.current = 'world'
    ref.current = 0
    with raises(TypeError):
        ref.current = []
    with raises(TypeError):
        ref.current = lambda: ...


def test_any():
    ref = Ref[Any]('hello')
    assert ref.current == 'hello'
    ref.current = 0
    ref.current = 0.


def test_empty_constructor():
    ref = Ref[float]()
    with raises(AttributeError):
        _ = ref.current
    ref.current = 0.
    assert ref.current == 0
    with raises(TypeError):
        ref.current = 'hello'


def test_generic_constraints():
    ref = Ref[list[str]](['hello'])
    ref = Ref[list[str]]()
    ref.current = ['hello']
    with raises(TypeError):
        ref.current = 'hello'


def test_typing_lib():
    ref = Ref[List]()
    ref.current = []
    with raises(TypeError):
        ref.current = 'hello'
    ref = Ref[Callable]()
    ref.current = lambda: 'hello'
    assert ref.current() == 'hello'
    with raises(TypeError):
        ref.current = 'hello'


def test_typing_with_generic():
    ref = Ref[List[str]](['hello'])
    with raises(TypeError):
        ref.current = 'hello'
    with raises(TypeError):
        ref.current = [lambda: None]
    ref = Ref[Callable[[], str]]()
    with raises(TypeError):
        ref.current = ['hello']
    ref.current = lambda: 'hello'
    ref.current = lambda: None # should not work in an ideal but hard to runtime check
    with raises(TypeError):
        ref.current = lambda x: x


def test_ellipsis():
    with raises(TypeError):
        ref = Ref(...)
    ref = Ref('hello')
    with raises(TypeError):
        ref.current = ...


def test_none():
    ref = Ref(None)
    ref.current = None
    with raises(TypeError):
        ref.current = 'hello'


def test_type():
    # note that it does not work a level deeper, eg. Type[Container[str]] with list[str]
    ref = Ref[Type[Container]]()
    ref.current = list
    ref.current = tuple
    with raises(TypeError):
        ref.current = int
    with raises(TypeError):
        ref.current = 'hello'


def test_literal():
    ref = Ref[Literal[1, 2, 3]]()
    ref.current = 1
    ref.current = 2
    ref.current = 3
    with raises(TypeError):
        ref.current = 4


def test_enum():
    TestEnum = Enum('TestEnum', 'ANT BEE')
    ref = Ref[TestEnum]()
    ref.current = TestEnum.ANT
    ref.current = TestEnum.BEE
    with raises(TypeError):
        ref.current = 0


def test_empty2():
    with raises(TypeError):
        ref = Ref()
