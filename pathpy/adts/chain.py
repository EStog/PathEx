from collections import deque
from collections.abc import Iterable, Iterator
from typing import TypeVar

_T = TypeVar('_T')


class Chain(Iterator[_T]):
    """A chain that can be expanded to the right and to the left.
    Chains behave like Python iterators. That means that they support `next` operation and can not be restarted once they are exhausted.

    >>> c = Chain()
    >>> c.expand_right([1, 2, 3])
    >>> c.expand_left(['a', 'b', 'c'])

    Single elements may be appended too.

    >>> c.put_left('x')
    >>> c.put_right('y')
    >>> c.expand_left([1, 2])
    >>> c.expand_right(['w', 'e'])
    >>> next(c)
    1
    >>> c.expand_left([3, 4])

    >>> assert list(c) == [3, 4, 2, 'x', 'a', 'b', 'c', 1, 2, 3, 'y', 'w', 'e']
    >>> try:
    ...     next(c)
    ... except StopIteration:
    ...     pass # Right!
    ... else:
    ...     print('Wrong!')

    """
    def __init__(self) -> None:
        self._elements = deque()

    def put_right(self, obj: object) -> None:
        self._elements.append(iter([obj]))

    def put_left(self, obj: object) -> None:
        self._elements.appendleft(iter([obj]))

    def expand_right(self, iterable: Iterable[_T]) -> None:
        self._elements.append(iter(iterable))

    def expand_left(self, iterable: Iterable[_T]) -> None:
        self._elements.appendleft(iter(iterable))

    def __next__(self) -> _T:
        while True:
            try:
                x = next(self._elements[0])
            except StopIteration:
                self._elements.popleft()
            except IndexError:
                raise StopIteration
            else:
                break
        return x
