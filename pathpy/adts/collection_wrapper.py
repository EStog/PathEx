from __future__ import annotations

import types
from typing import Callable, Iterable, Protocol, TypeVar

_T = TypeVar('_T')
_O = TypeVar('_O')


class CollectionWrapper(Protocol[_T, _O]):
    PopException: type[Exception]
    def __init__(self: CollectionWrapper[_T, _O]) -> None: ...
    def put(self: CollectionWrapper[_T, _O], obj: _O) -> None: ...
    def extend(self: CollectionWrapper[_T, _O], it: Iterable[_O]) -> None: ...
    def pop(self: CollectionWrapper[_T, _O]) -> _O: ...


def get_collection_wrapper(classs: type[_T],
                           put: Callable[[_T, _O], None] | None = None,
                           extend: Callable[[_T, Iterable[_O]],
                                            None] | None = None,
                           pop: Callable[[_T], _O] | None = None,
                           pop_exception: type[Exception] | None = None) -> type[CollectionWrapper[_T, _O]]:
    """Generates a class with a put-extend-pop interface

    This function is usefull for using with generators that expect this interface.

    Args:
        classs (type[_T]): The base class
        put (Callable[[_T, _O], None]): method to put one element
        extend (Callable[[_T, Iterable[_O]], None]): method to extend the collection with an iterable
        pop (Callable[[_T], _O]): method to take (and remove) an element.

    Returns:
        type[CollectionWrapper[_T, _O]]: The wrapped collection.

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
        if put:
            cls['put'] = put
        if extend:
            cls['extend'] = extend
        if pop:
            cls['pop'] = pop
            cls['PopException'] = pop_exception

    name = f'{classs.__name__[0].title()+classs.__name__[1:]}Wrapper'
    return types.new_class(name, (classs,), exec_body=exec_body)
