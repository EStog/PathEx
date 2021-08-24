from .term import Term
from dataclasses import dataclass

@dataclass(frozen=True)
class Letter(Term):
    value: object
