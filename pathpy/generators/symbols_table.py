from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import cast

from pathpy.expressions.terms.empty_string import EMPTY_STRING, EmptyString
from pathpy.expressions.terms.letters_unions.letters_negative_union import \
    LettersNegativeUnion as NU
from pathpy.expressions.terms.letters_unions.letters_possitive_union import \
    LettersPossitiveUnion as PU
from pathpy.expressions.terms.letters_unions.letters_union import \
    LettersUnion as LU
from pathpy.expressions.terms.term import Term
from pathpy.expressions.terms.wildcard import WILDCARD, Wildcard

from ._expressions._named_wildcard import NamedWildcard as NW


# TODO: Change type signatures from object to Term.
# TODO: Check copy of inmutables for efficiency reasons
# TODO: Use mutable collections.
@dataclass(frozen=True, eq=False)
class SymbolsTable:

    _wilds_of: dict[int, set[NW]] = \
        field(default_factory=dict)

    _group_of: dict[NW, int] = \
        field(default_factory=dict)

    _value_of: dict[int, Term] = \
        field(default_factory=dict)

    _wilds_cache: dict[int, tuple[NW, ...]] = \
        field(default_factory=dict)

    _wilds_amount: int = 0

    def get_wildcard(self, cache_id: int, number: int) -> tuple[NW, SymbolsTable]:
        cache = self._wilds_cache.setdefault(cache_id, tuple())
        if number == len(cache):
            wildcard = NW(self._wilds_amount)
            group = id(wildcard)
            return wildcard, replace(
                self,
                _group_of=self._group_of | {wildcard: group},
                _wilds_of=self._wilds_of | {group: {wildcard}},
                _wilds_cache=self._wilds_cache | {
                    cache_id: cache + (wildcard,)},
                _wilds_amount=self._wilds_amount + 1)
        else:
            return cache[number], self

    def get_concrete_value(self, o: NW) -> PU | NW:
        x = self._value_of.get(self._group_of[o], o)
        return x if isinstance(x, PU) else o

    def get_boundary_value(self, o: NW) -> Term:
        return self._value_of.get(self._group_of[o], o)

    @staticmethod
    def _get_letters_union(value: frozenset[object], Union: type[LU]) -> LU | None:
        return Union(value) if value != frozenset() else None

    def intersect(self, a1: Term, a2: Term) -> tuple[Term | None, SymbolsTable]:
        a1_type, a2_type = type(a1), type(a2)

        if a1_type == a2_type == NW:
            return self._intersect_nameds(a1, a2)
        elif a1_type == NW and a2_type != EmptyString:
            return self._intersect_named__term(a1, a2)
        elif a2_type == NW and a1_type != EmptyString:
            return self._intersect_named__term(a2, a1)
        else:
            return self._get_intersect_values(a1, a2), self

    def difference(self, a1: Term, a2: Term) -> tuple[Term | None, SymbolsTable, Term | None, SymbolsTable]:
        a1_type, a2_type = type(a1), type(a2)

        if a1_type == a2_type == NW:
            return self._bi_difference_nameds(a1, a2)
        elif a1_type == NW and a2_type != EmptyString:
            return self._bi_difference_named__term(a1, a2)
        elif a2_type == NW and a1_type != EmptyString:
            return self._bi_difference_named__term(a2, a1)
        else:
            x, y = self._get_bi_difference_values(a1, a2)
            return x, self, y, self

    def _get_intersect_values(self, a1: Term, a2: Term) -> Term | None:
        a1_type, a2_type = type(a1), type(a2)

        if a1_type == a2_type == EmptyString:
            return EMPTY_STRING
        elif a1_type == EmptyString or a2_type == EmptyString:
            return None
        elif (a1_type, a2_type) == (PU, PU):
            a1, a2 = cast(PU, a1), cast(PU, a2)
            return self._get_letters_union(a1.letters & a2.letters, PU)
        elif (a1_type, a2_type) == (PU, NU):
            a1, a2 = cast(PU, a1), cast(NU, a2)
            return self._get_letters_union(a1.letters - a2.letters, PU)
        elif (a1_type, a2_type) == (NU, PU):
            a1, a2 = cast(NU, a1), cast(PU, a2)
            return self._get_letters_union(a2.letters - a1.letters, PU)
        elif (a1_type, a2_type) == (NU, NU):
            a1, a2 = cast(NU, a1), cast(NU, a2)
            return self._get_letters_union(a1.letters | a2.letters, NU)
        elif a1_type == Wildcard and a2_type != Wildcard:
            return a2
        else:  # if a2_type == Wildcard:
            return a1

    def _get_bi_difference_values(self, a1: Term, a2: Term) -> tuple[Term | None, Term | None]:
        def _get_bi_difference_wildcard_value(t: type[Term], v: Term) -> LU | None:
            if t == PU:
                return cast(PU, v).as_negative()
            elif t == NU:
                return cast(NU, v).as_possitive()
            else:  # if t == Wildcard
                return None

        a1_type, a2_type = type(a1), type(a2)

        if a1_type == a2_type == EmptyString:
            return None, None
        elif a1_type == EmptyString:
            return EMPTY_STRING, a2
        elif a2_type == EmptyString:
            return a1, EMPTY_STRING
        elif (a1_type, a2_type) == (PU,  PU):
            a1, a2 = cast(PU, a1), cast(PU, a2)
            return (self._get_letters_union(a1.letters - a2.letters, PU),
                    self._get_letters_union(a2.letters - a1.letters, PU))
        elif (a1_type, a2_type) == (PU, NU):
            a1, a2 = cast(PU, a1), cast(NU, a2)
            return (self._get_letters_union(a1.letters & a2.letters, PU),
                    self._get_letters_union(a2.letters | a1.letters, NU))
        elif (a1_type, a2_type) == (NU, PU):
            a1, a2 = cast(NU, a1), cast(PU, a2)
            return (self._get_letters_union(a1.letters | a2.letters, NU),
                    self._get_letters_union(a2.letters & a1.letters, PU))
        elif (a1_type, a2_type) == (NU, NU):
            a1, a2 = cast(NU, a1), cast(NU, a2)
            return (self._get_letters_union(a2.letters - a1.letters, PU),
                    self._get_letters_union(a1.letters - a2.letters, PU))
        elif a1_type == Wildcard and a2_type != Wildcard:
            return _get_bi_difference_wildcard_value(a2_type, a2), None
        else:  # if a2_type == Wildcard:
            return None, _get_bi_difference_wildcard_value(a1_type, a1)

    def _get_more_concrete(self, group: int, value: Term | None, v) -> tuple[NW | None, SymbolsTable]:
        if value:
            return v, replace(self, _value_of=self._value_of | {group: value})
        else:
            return None, self

    def _intersect_named__term(
        self, a1: NW,
        a2: Term  # <- but not EmptyString
    ) -> tuple[NW | None, SymbolsTable]:
        group1 = self._group_of[a1]
        value1 = self._value_of.get(group1, WILDCARD)

        match = self._get_intersect_values(value1, a2)
        return self._get_more_concrete(group1, match, a1)

    def _bi_difference_named__term(
        self, a1: NW,
        a2: Term  # <- but not EmptyString
    ) -> tuple[NW | None, SymbolsTable, Term | None, SymbolsTable]:
        group1 = self._group_of[a1]
        value1 = self._value_of.get(group1, WILDCARD)

        value1, value2 = self._get_bi_difference_values(value1, a2)

        return *self._get_more_concrete(group1, value1, a1), value2, self

    def _intersect_nameds(self, a1: NW, a2: NW) -> tuple[NW | None, SymbolsTable]:
        group1, group2 = self._group_of[a1], self._group_of[a2]
        value1, value2 = self._value_of.get(
            group1, WILDCARD), self._value_of.get(group2, WILDCARD)

        match = self._get_intersect_values(value1, value2)
        if match is WILDCARD:
            updated_groups, wilds_of = self._bound_to(group1, group2)
            return a1, replace(self, _wilds_of=wilds_of, _group_of=self._group_of | updated_groups)
        elif match:
            updated_groups, wilds_of = self._bound_to(group1, group2)
            return a1, replace(self, _wilds_of=wilds_of, _group_of=self._group_of |
                               updated_groups, _value_of=self._value_of | {group1: match})
        else:
            return None, self

    def _bi_difference_nameds(self, a1: NW, a2: NW) -> tuple[NW | None, SymbolsTable, NW | None, SymbolsTable]:
        group1, group2 = self._group_of[a1], self._group_of[a2]
        value1, value2 = self._value_of.get(
            group1, WILDCARD), self._value_of.get(group2, WILDCARD)

        diff1, diff2 = self._get_bi_difference_values(value1, value2)
        r1, table1 = self._get_more_concrete(group1, diff1, a1)
        r2, table2 = self._get_more_concrete(group2, diff2, a2)
        return r1, table1, r2, table2

    def _bound_to(self, group1: int, group2: int) -> tuple[dict[NW, int], dict[int, set[NW]]]:
        wilds2 = self._wilds_of[group2]
        updated_groups = {x: group1 for x in wilds2}
        wilds_of = self._wilds_of.copy()
        del wilds_of[group2]
        wilds_of[group1] |= wilds2
        return updated_groups, wilds_of


__all__ = ['SymbolsTable']
