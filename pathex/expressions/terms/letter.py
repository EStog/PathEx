from dataclasses import dataclass
from pathex.expressions.expression import Expression

from .term import Term


@dataclass(frozen=True)
class Letter(Term):
    value: object

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        elif not isinstance(other, Expression):
            return self.value == other
        else:
            return False

    def __hash__(self):
        return hash(self.value)

    def __repr__(self) -> str:
        return repr(self.value)
