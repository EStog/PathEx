from __future__ import annotations

from dataclasses import dataclass


from pathpy.expressions.nary_operators.concatenation import Concatenation

@dataclass(frozen=True, init=False, eq=False)
class Tag(Concatenation):
    """A Tag identifies a region, where traces needs to be managed.

    A Tag is just a concatenation of two Labels objects, identifying the beginning and the end of the region.
    """

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


@dataclass(frozen=True, init=False, eq=False)
class Label:
    """This class represents an object that is part of a Tag.
    Label objects are used to identify the beginning and the end of a region
    """
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
