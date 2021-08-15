from __future__ import annotations

from functools import partial, singledispatchmethod
from math import inf
from typing import Iterator, cast
from collections.abc import Callable

from pathpy.adts.chain import Chain
from pathpy.adts.containers.head_tail_iterable import HeadTailIterable
from pathpy.expressions.expression import Expression
from pathpy.expressions.nary_operators.concatenation import Concatenation
from pathpy.expressions.nary_operators.intersection import Intersection
from pathpy.expressions.nary_operators.nary_operator import NAryOperator
from pathpy.expressions.nary_operators.shuffle import Shuffle
from pathpy.expressions.nary_operators.synchronization import Synchronization
from pathpy.expressions.nary_operators.union import Union
from pathpy.expressions.negation import Negation
from pathpy.expressions.repetitions.concatenation_repetition import \
    ConcatenationRepetition
from pathpy.expressions.repetitions.shuffle_repetition import ShuffleRepetition
from pathpy.expressions.substitution import Substitution
from pathpy.expressions.terms.empty_string import EMPTY_STRING
from pathpy.expressions.terms.letters_unions.letters_negative_union import \
    LettersNegativeUnion
from pathpy.expressions.terms.letters_unions.letters_possitive_union import \
    LettersPossitiveUnion
from pathpy.expressions.terms.term import Term
from pathpy.expressions.terms.wildcard import WILDCARD

from ._expressions._named_wildcard import NamedWildcard
from ._expressions._with_cached_wildcards import WithCachedWildcards
from .symbols_table import SymbolsTable

if __debug__:
    from .misc import NOT_EMPTY_STRING_MESSAGE

__all__ = ['AlternativesGenerator']

#TODO: Unify `table` and `extra` parameters.

class AlternativesGenerator(Iterator):

    def __init__(self, expression: object, table: SymbolsTable,
                 extra: object, not_normal: bool = False) -> None:
        self._visitor = self._get_visitor(expression, table, extra)
        self._alts: Chain[tuple[object, Expression,
                                SymbolsTable, object]] = Chain()
        if not_normal:
            self._next = partial(next, self._visitor)

    def __next__(self) -> tuple[object, Expression, SymbolsTable, object]:
        return self._next()

    def _next(self) -> tuple[object, Expression, SymbolsTable, object]:
        try:
            return next(self._alts)
        except StopIteration:
            head, tail, table, extra = next(self._visitor)
            if isinstance(head, NamedWildcard) and \
                    (value := table.get_concrete_value(head)) is not head:
                head = value
            if isinstance(head, LettersPossitiveUnion):
                head, rest = head.get_one_rest()
                self._alts.expand_right((x, tail, table, extra) for x in rest)
            return head, tail, table, extra

    @singledispatchmethod
    def _get_visitor(self, expression: object, table: SymbolsTable, extra: object) -> Iterator[tuple[Term, Expression, SymbolsTable, object]]:
        yield LettersPossitiveUnion({expression}), EMPTY_STRING, table, extra

    @_get_visitor.register(Callable)
    def _function_visitor(self, func: Callable[[SymbolsTable, object], tuple[object, SymbolsTable, object]], table: SymbolsTable, extra: object) -> Iterator[tuple[Term, Expression, SymbolsTable, object]]:
        exp, table, extra = func(table, extra)
        yield from self._get_visitor(exp, table, extra)

    @_get_visitor.register
    def _term_visitor(self, exp: Term, table: SymbolsTable, extra: object) -> Iterator[tuple[Term, Expression, SymbolsTable, object]]:
        yield exp, EMPTY_STRING, table, extra

    @_get_visitor.register
    def _union_visitor(self, exp: Union, table: SymbolsTable, extra: object) -> Iterator[tuple[Term, Expression, SymbolsTable, object]]:
        for e in exp:
            yield from self._get_visitor(e, table, extra)

    @_get_visitor.register
    def _negation_visitor(self, exp: Negation, table: SymbolsTable, extra: object) -> Iterator[tuple[Term, Expression, SymbolsTable, object]]:
        def negations_generator():
            nonlocal table, extra
            for head, tail, table, extra in self._get_visitor(exp.argument, table, extra):
                if tail:
                    yield Union(
                        Concatenation(Negation(head), tail),
                        Concatenation(head, Negation(tail)),
                        Concatenation(Negation(head), Negation(tail)))
                else:
                    yield Negation(head)

        argument_type = type(exp.argument)
        if argument_type is LettersPossitiveUnion:
            yield (cast(LettersPossitiveUnion, exp.argument).as_negative(),
                   EMPTY_STRING, table, extra)
        elif argument_type is LettersNegativeUnion:
            yield (cast(LettersNegativeUnion, exp.argument).as_possitive(),
                   EMPTY_STRING, table, extra)
        elif exp.argument is EMPTY_STRING:
            yield from self._get_visitor(ConcatenationRepetition(WILDCARD, 1, inf),
                                         table, extra)
        elif isinstance(exp.argument, NAryOperator):
            negations = HeadTailIterable(negations_generator())
            if negations.tail.head is not None:
                yield from self._get_visitor(Intersection(negations), table, extra)
            elif negations.head is not None:
                yield from self._get_visitor(negations.head, table, extra)

    @_get_visitor.register
    def _intersection_visitor(self, exp: Intersection, table: SymbolsTable, extra: object) -> Iterator[tuple[Term, Expression, SymbolsTable, object]]:
        if exp.head is not None:
            if exp.tail.head is None:
                yield from self._get_visitor(exp.head, table, extra)
                return

            # cached_alts_generator = CachedGenerator(self._get_visitor)

            for head1, tail1, table, extra in self._get_visitor(exp.head, table, extra):
                for head2, tail2, table, extra in self._get_visitor(exp.tail, table, extra):
                    # `aA & bB = (a & b) + (A & B)`
                    tail = EMPTY_STRING if tail1 is tail2 is EMPTY_STRING \
                        else Intersection(tail1, tail2)
                    # `a & b = a`                 if `a == b`
                    head, table = table.intersect(head1, head2)
                    if head:
                        yield head, tail, table, extra
                    # `a & b = {}`                if `a != b`

    @_get_visitor.register
    def _synchronization_visitor(self, exp: Synchronization, table: SymbolsTable, extra: object) -> Iterator[tuple[Term, Expression, SymbolsTable, object]]:
        if exp.head is not None:
            if exp.tail.head is None:
                yield from self._get_visitor(exp.head, table, extra)
                return

            # cached_alts_generator = CachedGenerator(alts_generator)

            for head1, tail1, table, extra in self._get_visitor(exp.head, table, extra):
                for head2, tail2, table, extra in self._get_visitor(exp.tail, table, extra):
                    # `aA @ bB = (a @ b) + (A @ B)`
                    tail = EMPTY_STRING if tail1 is tail2 is EMPTY_STRING \
                        else Synchronization(tail1, tail2)
                    # `a @ b = a`                     if `a == b`
                    head, table = table.intersect(head1, head2)
                    if head:
                        yield head, tail, table, extra
                    # `a @ b = a // b`                if `a != b`
                    h1, t1, h2, t2 = table.difference(head1, head2)
                    if h1:
                        yield from self._get_visitor(Concatenation(Shuffle(h1, head2), tail), t1, extra)
                    if h2:
                        yield from self._get_visitor(Concatenation(Shuffle(head1, h2), tail), t2, extra)

    @_get_visitor.register
    def _concatenation_visitor(self, exp: Concatenation, table: SymbolsTable, extra: object) -> Iterator[tuple[Term, Expression, SymbolsTable, object]]:
        if exp.head is not None:
            if exp.tail.head is None:
                yield from self._get_visitor(exp.head, table, extra)
                return

            for head, tail, table, extra in self._get_visitor(exp.head, table, extra):
                tail = exp.tail if tail is EMPTY_STRING \
                    else Concatenation(tail, exp.tail)
                if head is EMPTY_STRING:
                    yield from self._get_visitor(tail, table, extra)
                else:
                    yield head, tail, table, extra

    @_get_visitor.register
    def _concatenation_repetition_visitor(self, exp: ConcatenationRepetition, table: SymbolsTable, extra: object) -> Iterator[tuple[Term, Expression, SymbolsTable, object]]:
        assert exp.argument is not EMPTY_STRING, NOT_EMPTY_STRING_MESSAGE

        # a+1 = a
        if exp.lower_bound == exp.upper_bound == 1:
            return self._get_visitor(exp.argument, table, extra)

        # a*n = empty | a*[1,n]
        elif exp.lower_bound == 0:
            return self._get_visitor(Union(EMPTY_STRING,
                                           ConcatenationRepetition(
                                               exp.argument,
                                               1, exp.upper_bound)),
                                     table, extra)

        # a*[n,m] = a + a*[n-1,m-1] where n > 0
        else:
            return self._get_visitor(Concatenation.new(exp.argument,
                                                       ConcatenationRepetition(
                                                           exp.argument,
                                                           exp.lower_bound-1,
                                                           exp.upper_bound-1)),
                                     table, extra)

    @_get_visitor.register
    def _shuffle_visitor(self, exp: Shuffle, table: SymbolsTable, extra: object) -> Iterator[tuple[Term, Expression, SymbolsTable, object]]:
        if exp.head is not None:
            if exp.tail.head is None:
                yield from self._get_visitor(exp.head, table, extra)
                return

            def shuffle(x, y, table, extra):
                for head, tail, table, extra in self._get_visitor(x, table, extra):
                    # aA // B = a + (A // B) | ...
                    if tail is not EMPTY_STRING:
                        yield head, Shuffle(tail, y), table, extra
                    else:
                        # a // B = a + B | ...
                        yield head, y, table, extra

            yield from shuffle(exp.head, exp.tail, table, extra)
            yield from shuffle(exp.tail, exp.head, table, extra)

    @_get_visitor.register
    def _shuffle_repetition_visitor(self, exp: ShuffleRepetition, table: SymbolsTable, extra: object) -> Iterator[tuple[Term, Expression, SymbolsTable, object]]:
        assert exp.argument is not EMPTY_STRING, NOT_EMPTY_STRING_MESSAGE

        # a//1 = a
        if exp.lower_bound == exp.upper_bound == 1:
            yield from self._get_visitor(exp.argument, table, extra)

        # a%n = empty | a%[1,n]
        elif exp.lower_bound == 0:
            yield from self._get_visitor(Union(EMPTY_STRING,
                                               ShuffleRepetition(
                                                   exp.argument,
                                                   1, exp.upper_bound)),
                                         table, extra)
        else:
            for head, tail, table, extra in self._get_visitor(exp.argument, table, extra):

                # (aB)%[n,m] = a*[n,m] if `B` is empty string
                if tail is EMPTY_STRING:
                    yield from self._get_visitor(exp.as_concatenation_repetition(), table, extra)

                # = a + (B // aB%[n-1,m-1] ) where n > 0
                else:
                    yield (head,
                           Shuffle(tail,
                                   ShuffleRepetition(
                                       exp.argument,
                                       exp.lower_bound-1,
                                       exp.upper_bound-1)),
                           table, extra)

    @_get_visitor.register
    def _with_cached_wildcards_visitor(self, exp: WithCachedWildcards, table: SymbolsTable, extra: object) -> Iterator[tuple[Term, Expression, SymbolsTable, object]]:
        for head, tail, table, extra in self._get_visitor(exp.expression, table, extra):
            number = exp.number
            if head is WILDCARD:
                head, table = table.get_wildcard(exp.cache_id, exp.number)
                number += 1

            if tail is not EMPTY_STRING:
                tail = WithCachedWildcards(tail, number, exp.cache_id)

            yield head, tail, table, extra

    @_get_visitor.register
    def _substitution_visitor(self, exp: Substitution, table: SymbolsTable, extra: object) -> Iterator[tuple[Term, Expression, SymbolsTable, object]]:
        assert exp is not EMPTY_STRING, NOT_EMPTY_STRING_MESSAGE

        def get_gen_alt(head, replacements):
            nonlocal exp_tail
            if exp_tail is not EMPTY_STRING:
                exp_tail = Substitution(exp_tail, replacements)

            return head, exp_tail, table, extra

        for exp_head, exp_tail, table, extra in self._get_visitor(exp.argument, table, extra):
            if isinstance(exp_head, LettersPossitiveUnion):
                for exp_head in exp_head.letters:
                    # if there is nothing to replace
                    if (repl := exp.replacements.get(exp_head, exp_head)) is exp_head:
                        yield get_gen_alt(LettersPossitiveUnion({exp_head}), exp.replacements)
                    else:
                        if not isinstance(repl, (WithCachedWildcards, NamedWildcard)):
                            repl = WithCachedWildcards(repl, 0)
                        for repl_head, repl_tail, table, extra in self._get_visitor(repl, table, extra):
                            # a[D,a:r]     = r
                            # (aA)[D,a:r]  = r + A[D,a:r]
                            if repl_tail is EMPTY_STRING:
                                replacements = exp.replacements | {
                                    exp_head: repl_head}
                                yield get_gen_alt(repl_head, replacements)
                            else:
                                # a[D,a:rR] = r + R
                                if exp_tail is EMPTY_STRING:
                                    yield repl_head, repl_tail, table, extra
                                # (aA)[D,a:rR] = r + R + A[D,a:rR]
                                # where `r` may be a cached previous NamedWildcard
                                else:
                                    replacements = exp.replacements | {
                                        exp_head: Concatenation(repl_head, repl_tail)}
                                    yield (repl_head,
                                           Concatenation(
                                               repl_tail,
                                               Substitution(exp_tail, replacements)),
                                           table, extra)
            else:
                yield get_gen_alt(exp_head, exp.replacements)
