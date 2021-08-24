from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from functools import wraps

from pathpy.expressions.expression import Expression
from pathpy.generation.machines.machine import MachineWithMatch

from .tag import Tag

__all__ = ['Manager']

# TODO: refactor by using Shuffle and Intersection


class Manager(ABC):
    """A generic abstract manager.
    """

    def __init__(self, expression: Expression, machine: MachineWithMatch):
        self._alternatives = set()
        self._alternatives.add(expression)
        self._machine = machine

    @abstractmethod
    def _when_requested_match(self, label: object) -> object: ...

    @abstractmethod
    def _when_matched(self, label: object, label_info: object) -> object: ...

    @abstractmethod
    def _when_not_matched(self, label: object,
                          label_info: object) -> object: ...

    def match(self, label: object) -> object:
        """ This method is used to notify to the manager the presence of a given label.

        The manager then see if this label is allowed by checking if the internal expression can generate the given label.
        If the label is allowed or not, a respective action is taken.

        Args:
            label (object): The label to check for.
        """
        label_info = self._when_requested_match(label)
        if self._advance(label):
            return self._when_matched(label, label_info)
        else:
            return self._when_not_matched(label, label_info)

    def _advance(self, label: object) -> bool:
        new_alternatives = set()
        for exp in self._alternatives:
            for head, tail in self._machine.branches(exp):
                match = self._machine.match(label, head)
                if match is not None:
                    assert match == label, \
                        f'Match is {match} instead of label "{label}"'
                    new_alternatives.add(tail)
        if new_alternatives:
            self._alternatives = new_alternatives
            return True
        else:
            return False

    def register(self, tag: Tag, func=None):
        """Decorator to mark a method as a region.

        Args:
            tag (Tag): A tag to mark the given funcion with.
        """
        def wrapper(wrapped):
            @wraps(wrapped)
            def f(*args, **kwargs):
                self.match(tag.enter)
                x = wrapped(*args, **kwargs)
                self.match(tag.exit)
                return x
            return f

        if func is None:
            return wrapper
        else:
            return wrapper(func)

    @contextmanager
    def region(self, tag: Tag):
        """Context manager to mark a piece of code as a region.

        Args:
            tag (Tag): A tag to mark the corresponding block with.
        """
        self.match(tag.enter)
        try:
            yield self
        finally:
            self.match(tag.exit)
