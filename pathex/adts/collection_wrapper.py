from __future__ import annotations

import types
from typing import Any, Callable, Iterable, Iterator, Protocol, TypeVar

__all__ = ['CollectionWrapper']

_T = TypeVar('_T')
_O = TypeVar('_O')


class CollectionWrapper(Protocol[_O]):
    PopException: type[Exception]

    def __init__(self: CollectionWrapper[_O],
                 _it: Iterable[_O] = ...) -> None: ...
    def __add__(
        self, other: CollectionWrapper[_O] | _T) -> CollectionWrapper[_O] | _T: ...

    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[_O]: ...
    def __contains__(self, _o: Any) -> bool: ...

    def put(self: CollectionWrapper[_O], obj: _O) -> None: ...
    def extend(self: CollectionWrapper[_O], it: Iterable[_O]) -> None: ...
    def pop(self: CollectionWrapper[_O]) -> _O: ...


def get_collection_wrapper(parent: type[_T],
                           put: Callable[[_T, _O], None] | None = None,
                           extend: Callable[[_T, Iterable[_O]],
                                            None] | None = None,
                           pop: Callable[[_T], _O] | None = None,
                           pop_exception: type[Exception] | None = None,
                           __contains__: Callable[[
                               _T, Any], bool] | None = None,
                           __len__: Callable[[_T], int] | None = None,
                           __iter__: Callable[[_T], Iterator[_O]] | None = None) -> type[CollectionWrapper[_O]]:
    """Generates a class adaptor with a put-extend-pop-add interface

    This adaptor factory is usefull for using with classes that expect WrapperCollection interface.

    >>> def test(T):
    ...     l = T([1, 2, 3])
    ...     l.put(4)
    ...     l.extend([5, 6, 7])
    ...     assert l.pop() == 7
    ...     assert list(l) == [1, 2, 3, 4, 5, 6]
    ...     for i in range(6, 0, -1):
    ...         try:
    ...             assert l.pop() == i
    ...         except l.PopException:
    ...             assert i == 0
    ...             break
    ...     assert list(l) == []
    >>> List = get_collection_wrapper(list, list.append, list.extend, list.pop, IndexError)
    >>> test(List)
    >>> from collections import deque
    >>> Deque = get_collection_wrapper(deque, deque.append, deque.extend, deque.pop, IndexError)
    >>> test(Deque)
    """

    def exec_body(cls):
        cls.update(parent.__dict__)
        if put:
            cls['put'] = put
        if extend:
            cls['extend'] = extend
        if pop:
            cls['pop'] = pop
            cls['PopException'] = pop_exception
        if __contains__:
            cls['__contains__'] = __contains__
        if __len__:
            cls['__len__'] = __len__
        if __iter__:
            cls['__iter__'] = __iter__

    name = f'{parent.__name__[0].title()+parent.__name__[1:]}Wrapper'
    return types.new_class(name, (parent,), exec_body=exec_body)
