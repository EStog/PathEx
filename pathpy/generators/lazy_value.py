from ._expressions._named_wildcard import NamedWildcard
from .symbols_table import SymbolsTable


class LazyValue:

    def __init__(self, wildcard: NamedWildcard, table: SymbolsTable,
                 letters_generator, max_lookahead: int):
        from .letters_generator import LettersGenerator
        self._wildcard = wildcard
        self._table = table
        self._letters_generator: LettersGenerator = letters_generator
        self.max_lookahead = max_lookahead

    def get_value(self) -> object:
        def advanced(i):
            if i < self.max_lookahead and \
                    self._table.get_concrete_value(self._wildcard) is self._wildcard:
                table = self._letters_generator.advance_once()
                if table:
                    self._table = table
                    return True
            return False

        i = 0
        while advanced(i):
            i += 1
        return self._table.get_boundary_value(self._wildcard)

    def __str__(self) -> str:
        return str(self.get_value())
