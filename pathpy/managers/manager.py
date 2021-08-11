from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from functools import wraps
from typing import Iterator

from pathpy.expressions.expression import Expression
from pathpy.expressions.terms.letters_unions.letters_possitive_union import \
    LettersPossitiveUnion
from pathpy.generators._expressions._named_wildcard import NamedWildcard
from pathpy.generators.alternatives_generator import AlternativesGenerator
from pathpy.generators.symbols_table import SymbolsTable

from .tag import Tag

__all__ = ['Manager']

# TODO: refactor by using Shuffle and Intersection


class Manager(ABC):
    """A generic abstract manager.
    """

    def __init__(self, expression: Expression):
        self._alternatives = set()
        self._alternatives.add((expression, SymbolsTable()))

    @abstractmethod
    def _when_allowed(self, label: object) -> object: ...

    @abstractmethod
    def _when_not_allowed(self, label: object) -> object: ...

    def check(self, label: object) -> object:
        """ This method is used to notify to the manager the presence of a given label.

        The manager then see if this label is allowed by checking if the internal expression can generate the given label.
        If the label is allowed or not, a respective action is taken.

        Args:
            label (object): The label to check for.
        """
        if self._advance(label):
            return self._when_allowed(label)
        else:
            return self._when_not_allowed(label)

    def _advance(self, label: object) -> bool:
        def _assert_right_match(label, match, table):
            if isinstance(match, NamedWildcard):
                return match == table.get_value(match)
            elif isinstance(match, LettersPossitiveUnion):
                return match == label
            else:
                return False

        label = LettersPossitiveUnion({label})

        new_alternatives = set()
        for exp, table in self._alternatives:
            for head, tail, table in AlternativesGenerator(exp, table, not_normal=True):
                match, table = table.intersect(head, label)
                if match is not None:
                    assert _assert_right_match(label, match, table), \
                        f'Match is {match} instead of label "{label}"'
                    new_alternatives.add((tail, table))
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
                self.check(tag.enter)
                x = wrapped(*args, **kwargs)
                self.check(tag.exit)
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
        self.check(tag.enter)
        try:
            yield self
        finally:
            self.check(tag.exit)

    @classmethod
    def tags(cls, n: int) -> Iterator[Tag]:
        """Factory method that gives `n` tags.

        The names of the tags are the same as its object ids.

        Args:
            n (int): The amount of tags to be constructed

        Returns:
            Iterator[Tag]: an iterator that gives `n` anonymous tags.
        """
        return (Tag() for _ in range(n))

    @classmethod
    def named_tags(cls, *names: object) -> Iterator[Tag]:
        """Factory method that gives named tags.

        Args:
            *names (tuple[object]): The names for the constructed tags

        Returns:
            Iterator[Tag]: an iterator that gives tags with the given names.
        """
        return (Tag(name=name) for name in names)
