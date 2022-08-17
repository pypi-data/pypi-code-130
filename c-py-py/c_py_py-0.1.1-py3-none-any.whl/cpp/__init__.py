from typing import Any, Callable, Literal, NoReturn, Optional, Type, TypeVar, overload

from iife import iife
from typing_extensions import Self


class _Commentable:
    def __floordiv__(self, other: Any) -> NoReturn:
        print(end='')


@iife
class cpp(_Commentable):
    def __getitem__(self, other: slice):
        return other.step


@iife
class std:
    ...


@iife
class auto:
    def __and__(self, other: Any) -> Any:
        return other


@iife
class endl(_Commentable):
    ...


@iife
class cout(_Commentable):
    def __lshift__(self, other: Any) -> Self:
        if other is endl:
            print()
        else:
            print(other, end="")
        return self

    def __repr__(self) -> str:
        return ""


T = TypeVar("T")


class std_vector(list[T], _Commentable):
    @overload
    def __init__(
        self,
        initializer_list_or_size: set[T] | list[T],
        value: None = None,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        initializer_list_or_size: int,
        value: T,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        initializer_list_or_size: None = None,
        value: None = None,
    ) -> None:
        ...

    def __init__(
        self,
        initializer_list_or_size: Optional[set[T] | list[T] | int] = None,
        value: Optional[T] = None,
    ) -> None:

        self.size: Callable[[], int] = lambda: len(self)
        self.empty: Callable[[], bool] = lambda: len(self) == 0
        self.clear: Callable[[], None] = lambda: self.__init__()
        self.resize: Callable[[int, T], None] = lambda n, v: self.__init__(n, v)

        if isinstance(initializer_list_or_size, int):
            assert value is not None, "Must provide value for vector of size {}".format(
                initializer_list_or_size
            )
            self._datatype: Type[T] = type(value)
            super().__init__([value] * initializer_list_or_size)
        elif initializer_list_or_size is not None:
            self._datatype: Type[T] = type(next(iter(initializer_list_or_size)))
            super().__init__(initializer_list_or_size)
        else:
            self._datatype = None
            super().__init__()

    def __lt__(self, template_param: Type[T]) -> Self:
        if not self._datatype:
            self._datatype = template_param
        else:
            try:
                return std_vector(list(template_param(i._value) for i in self))
            except Exception as e:
                raise TypeError(
                    f"Cannot construct vector of type {template_param} from arguments of type {self._datatype}"
                )
        return self

    def push_back(self, value) -> Self:
        self.append(value)
        return self

    def back(self) -> T:
        return self.__getitem__(-1)

    def front(self) -> T:
        return self.__getitem__(0)

    def pop_back(self) -> Self:
        self.pop(-1)
        return self

    def at(self, i: int) -> T:
        return self[i]

    def __iter__(self) -> "element_ref":
        return element_ref(self)


class element_ref:
    def __init__(self, vector: std_vector[T], idx=0) -> None:
        self._vector = vector
        self._index: int = idx

    def __next__(self) -> Self:
        if self._index >= len(self._vector):
            raise StopIteration
        else:
            self._index += 1
            return self

    def __repr__(self) -> str:
        return self._vector[self._index - 1].__repr__()

    def __iadd__(self, other: Any) -> Self:
        self._vector[self._index - 1] += other
        return self

    @property
    def _value(self):
        return self._vector[self._index - 1]


@iife
class vector:
    def __lt__(self, _: type) -> Literal[True]:
        return True


# Type aliases
v = std_vector

# fmt: off
if __name__ == "__main__":
    # include <iostream>
    # include <vector>

    # TODO: support c++-y classes
    # class MyClass:
    #     @public
    #     def getData(self):
    #         return self.data
        
    #     @private
    #     data: int = 0

    (cpp) // "Construct a vector from an initializer list"
    x: std_vector[int] = (cpp) [std::vector<int>v({1, 2, 3})]  # type: ignore

    x.push_back(4) // "Adds 4 to the end of the vector"

    (cpp) [std::cout] << "Vector x: " << x << (cpp) [std::endl] // "prints out [1, 2, 3, 4]"
    

    (cpp) // "Loop over references to elements of x:"
    for i in auto& x:
        (cpp) [std::cout] << "Incrementing " << i << "..." << (cpp) [std::endl]
        i += 1

    (cpp) [std::cout] << "Vector after: " << x << (cpp) [std::endl]
