import typing
from dataclasses import dataclass

__all__ = ['Label']


@dataclass(frozen=True)
class Label:
    """This class represents an object that is part of a Tag.
    Label objects are used as check points in the execution of the program.
    """
    name: typing.Union[int, str]
    kind: str

    def _track_request(self):
        # nothing to be done here
        pass

    def _track_allowed(self):
        # nothing to be done here
        pass

    def _track_denied(self):
        # nothing to be done here
        pass

    def __repr__(self) -> str:
        return f'{self.kind}({self.name})'

    def __hash__(self) -> int:
        return id(self)
