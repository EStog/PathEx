from __future__ import annotations

import types
from typing import Callable, Iterable, Protocol, TypeVar

__all__ = ['CollectionWrapper']

_T = TypeVar('_T')
_O = TypeVar('_O')
_X = TypeVar('_X')


class CollectionWrapper(Protocol[_O]):
    PopException: type[Exception]
    def __init__(self: CollectionWrapper[_O]) -> None: ...
    def __add__(self: CollectionWrapper[_O],
                other: CollectionWrapper[_O] | _T) -> CollectionWrapper[_O] | _T: ...

    def put(self: CollectionWrapper[_O], obj: _O) -> None: ...
    def extend(self: CollectionWrapper[_O], it: Iterable[_O]) -> None: ...
    def pop(self: CollectionWrapper[_O]) -> _O: ...


def get_collection_wrapper(parent: type[_T],
                           put: Callable[[_T, _O], None] | None = None,
                           extend: Callable[[_T, Iterable[_O]],
                                            None] | None = None,
                           pop: Callable[[_T], _O] | None = None,
                           pop_exception: type[Exception] | None = None) -> type[CollectionWrapper[_O]]:
    """Generates a class adaptor with a put-extend-pop-add interface

    This adaptor factory is usefull for using with classes that expect WrapperCollection interface.

    Args:
        parent (type[_T]): The base class
        put (Callable[[_T, _O], None] | None): method to put one element
        extend (Callable[[_T, Iterable[_O]], None]| None): method to extend the collection with an iterable
        pop (Callable[[_T], _O]): method to take (and remove) an element
        add (Callable[[_T, _T|_X], _T|_X] | None): method to implement __add__

    Returns:
        type[CollectionWrapper[_O]]: The wrapped collection.

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
    def __repr__(self):
        return name
    def exec_body(cls):
        cls.update(parent.__dict__)
        if put:
            cls['put'] = put
        if extend:
            cls['extend'] = extend
        if pop:
            cls['pop'] = pop
            cls['PopException'] = pop_exception

    name = f'{parent.__name__[0].title()+parent.__name__[1:]}Wrapper'
    return types.new_class(name, (parent,), exec_body=exec_body)
