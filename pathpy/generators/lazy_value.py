from pathpy.expressions.expression import Expression
from pathpy.expressions.terms.letters_unions.letters_possitive_union import \
    LettersPossitiveUnion

from ._expressions._named_wildcard import NamedWildcard
from .symbols_table import SymbolsTable


class LazyValue:

    def __init__(self, wildcard: NamedWildcard,
                 tail: Expression, table: SymbolsTable, extra: object,
                 pos: int, letters_generator, max_lookahead: int):
        from .letters_generator import LettersGenerator
        self._wildcard = wildcard
        self._tail = tail
        self._table = table
        self._extra = extra
        self._pos = pos
        self._letters_generator: LettersGenerator = letters_generator
        self.max_lookahead = max_lookahead

    @property
    def value(self) -> object:
        def advanced(i):
            if i < self.max_lookahead and \
                    self._table.get_concrete_value(self._wildcard) is self._wildcard:
                tail, table, extra = self._letters_generator.advance_once()
                if (tail, table, extra) != (None, None, None):
                    self._tail = tail
                    self._table = table
                    self._extra = extra
                    return True
            return False

        i = 0
        while advanced(i):
            i += 1
        return self._break_up(self._table.get_boundary_value(self._wildcard))

    def _break_up(self, term):
        if isinstance(term, LettersPossitiveUnion):
            term, rest = term.get_one_rest()
            self._letters_generator.update(term, rest, self._pos,
                                           self._tail, self._table,
                                           self._extra)
        return term
