from dataclasses import dataclass

from pathpy.expressions.expression import Expression


@dataclass(frozen=True)
class WithCachedWildcards(Expression):
    expression: object
    number: int
    cache_id: int = -1

    def __post_init__(self):
        if self.cache_id == -1:
            object.__setattr__(self, 'cache_id', id(self))

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.expression!r}, {self.cache_id!r}, {self.number!r})'
