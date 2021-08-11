from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Iterator

from pathpy.expressions.expression import Expression
from pathpy.expressions.nary_operators.concatenation import Concatenation
from pathpy.expressions.terms.letters_unions.letters_possitive_union import \
    LettersPossitiveUnion
from pathpy.generators._expressions._named_wildcard import NamedWildcard
from pathpy.generators.alternatives_generator import AlternativesGenerator
from pathpy.generators.symbols_table import SymbolsTable

__all__ = ['Manager']


@dataclass(frozen=True, init=False, eq=False)
class Label:
    parent: Tag

    def __repr__(self) -> str:
        if hasattr(self.parent, 'name'):
            return f'{self.__class__.__name__[1:]}({self.parent.name})'
        else:
            return f'{self.__class__.__name__[1:]}({id(self.parent)})'

    def __hash__(self) -> int:
        return id(self)


class Enter(Label):
    pass


class Exit(Label):
    pass


@dataclass(frozen=True, init=False, eq=False)
class Tag(Concatenation):

    enter: Label
    exit: Label

    def __new__(cls, *args, name=None):
        if args:
            return super().__new__(cls, *args)
        enter = Enter()
        exit = Exit()
        self = super().__new__(cls, enter, exit)

        if name is not None:
            object.__setattr__(self, 'name', name)

        object.__setattr__(enter, 'parent', self)
        object.__setattr__(exit, 'parent', self)
        object.__setattr__(self, 'enter', enter)
        object.__setattr__(self, 'exit', exit)
        return self

    def __repr__(self) -> str:
        if hasattr(self, 'name'):
            return f'{self.__class__.__name__[1:]}({self.name})'
        else:
            return f'{self.__class__.__name__[1:]}({id(self)})'

    def __hash__(self) -> int:
        return id(hash)


class Manager(ABC):
    """A generic abstract manager
    """

    def __init__(self, expression: Expression):
        self._alternatives = set()
        self._alternatives.add((expression, SymbolsTable()))

    @abstractmethod
    def _when_allowed(self, label: object) -> None: ...

    @abstractmethod
    def _when_not_allowed(self, label: object) -> None: ...

    def check(self, label: object) -> None:
        """ This method is used to notify to the manager the presence of a given label.

        The manager then see if this label is allowed by checking if the internal expression can generate the given label.
        If the label is allowed or not, a respective action is taken.

        Args:
            label (object): The label to check for.
        """
        if self._advance(label):
            self._when_allowed(label)
        else:
            self._when_not_allowed(label)

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
        """Decorator to mark a method as a concurrent unit of execution

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
        """Context manager to mark a piece of code as a concurrent unit of execution

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
            names (tuple[object]): The names for the constructed tags

        Returns:
            Iterator[Tag]: an iterator that gives tags with the given names.
        """
        return (Tag(name=name) for name in names)
