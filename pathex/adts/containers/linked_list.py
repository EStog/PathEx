from __future__ import annotations

from collections.abc import Reversible
from dataclasses import dataclass, field, replace
from functools import partial
from typing import Callable, Generic, Hashable, Iterable, Iterator, TypeVar

_E = TypeVar("_E", bound=Hashable)


class Node(Generic[_E]):
    def _new(self, node, a, b):
        self = replace(self, **{a: None})
        node = replace(node, **{b: None})
        object.__setattr__(self, a, node)
        object.__setattr__(node, b, self)
        return self


@dataclass(frozen=True)
class WithNextNode(Node[_E]):
    next: Node[_E] | None = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "next", None)

    def new_next(self, node: WithPreviousNode[_E]) -> WithNextNode[_E]:
        return self._new(node, "next", "previous")


@dataclass(frozen=True)
class WithPreviousNode(Node[_E]):
    previous: Node[_E] | None = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "previous", None)

    def new_previous(self, node: WithNextNode[_E]) -> WithPreviousNode[_E]:
        return self._new(node, "previous", "next")


@dataclass(frozen=True)
class ValueNode(WithPreviousNode[_E], WithNextNode[_E]):
    value: _E


@dataclass(frozen=True)
class LinkedList(Reversible[_E]):
    begin: WithNextNode[_E]
    end: WithPreviousNode[_E]

    def __new__(cls, iterable: Iterable[_E]):
        self = object.__new__(cls)
        begin = WithNextNode()
        end = WithPreviousNode()
        begin.new_next(end)
        object.__setattr__(self, "begin", begin)
        object.__setattr__(self, "end", end)
        object.__setattr__(self, 'hash', hash((WithNextNode, WithPreviousNode, LinkedList)))
        for e in iterable:
            self = self.new_last(e)
        return self

    def __iter__(self) -> Iterator[_E]:
        return LinkedListForwardIterator(self.begin)

    def __reversed__(self) -> Iterator[_E]:
        return LinkedListReversedIterator(self.end)

    def new_last(self, value: _E) -> LinkedList[_E]:
        return replace(self, end=self.end.new_previous(ValueNode(value)))

    def new_first(self, value: _E) -> LinkedList[_E]:
        return replace(self, begin=self.begin.new_next(ValueNode(value)))

    def __add__(self, other: LinkedList[_E]) -> LinkedList[_E]:
        pass


class LinkedListIterator(Iterator[_E]):
    _current_node: Node[_E]

    def _advance(self, give_adjacent: Callable[[Node[_E]], Node[_E]]) -> _E:
        adjacent = give_adjacent(self._current_node)
        assert (
            isinstance(adjacent, Node) and type(adjacent) is not Node
        ), "Corrupted linked list with a hole or without extreme node"
        if isinstance(adjacent, ValueNode):
            self._current_node = adjacent
            return adjacent.value
        else:
            if __debug__:
                try:
                    assert give_adjacent(self._current_node)
                except AttributeError:
                    pass
                else:
                    raise AssertionError("Corrupted linked list with wrong node")
            raise StopIteration


@dataclass
class LinkedListForwardIterator(LinkedListIterator[_E]):
    _current_node: WithNextNode[_E]

    def __next__(self) -> _E:
        return self._advance(partial(getattr, name="next"))


@dataclass
class LinkedListReversedIterator(LinkedListIterator[_E]):
    _current_node: WithPreviousNode[_E]

    def __next__(self) -> _E:
        return self._advance(partial(getattr, name="previous"))
