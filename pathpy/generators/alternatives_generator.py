from __future__ import annotations

from functools import partial, singledispatchmethod
from math import inf
from typing import Iterator, cast

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


class AlternativesGenerator(Iterator):

    def __init__(self, expression: object, table: SymbolsTable | None = None, not_normal=False) -> None:
        if table is None:
            table = SymbolsTable()
        self._visitor = self._get_visitor(expression, table)
        self._alts: Chain[tuple[object, Expression, SymbolsTable]] = Chain()
        if not_normal:
            self._next = partial(next, self._visitor)

    def __next__(self) -> tuple[object, Expression, SymbolsTable]:
        return self._next()

    def _next(self) -> tuple[object, Expression, SymbolsTable]:
        try:
            return next(self._alts)
        except StopIteration:
            head, tail, table = next(self._visitor)
            if isinstance(head, NamedWildcard) and (value := table.get_concrete_value(head)) is not head:
                head = value
            if isinstance(head, LettersPossitiveUnion):
                head, rest = head.get_one_rest()
                self._alts.expand_right((x, tail, table) for x in rest)
            return head, tail, table

    @singledispatchmethod
    def _get_visitor(self, expression: object, table: SymbolsTable) -> Iterator[tuple[Term, Expression, SymbolsTable]]:
        yield LettersPossitiveUnion({expression}), EMPTY_STRING, table

    @_get_visitor.register
    def _term_visitor(self, exp: Term, table: SymbolsTable):
        yield exp, EMPTY_STRING, table

    @_get_visitor.register
    def _union_visitor(self, exp: Union, table: SymbolsTable):
        for e in exp:
            yield from self._get_visitor(e, table)

    @_get_visitor.register
    def visit_negation(self, exp: Negation, table: SymbolsTable):
        def negations_generator():
            nonlocal exp, table
            for head, tail, table in self._get_visitor(exp.argument, table):
                if tail:
                    yield Union(
                        Concatenation(Negation(head), tail),
                        Concatenation(head, Negation(tail)),
                        Concatenation(Negation(head), Negation(tail)))
                else:
                    yield Negation(head)

        argument_type = type(exp.argument)
        if argument_type is LettersPossitiveUnion:
            yield cast(LettersPossitiveUnion, exp.argument).as_negative(), EMPTY_STRING, table
        elif argument_type is LettersNegativeUnion:
            yield cast(LettersNegativeUnion, exp.argument).as_possitive(), EMPTY_STRING, table
        elif exp.argument is EMPTY_STRING:
            yield from self._get_visitor(ConcatenationRepetition(WILDCARD, 1, inf), table)
        elif isinstance(exp.argument, NAryOperator):
            negations = HeadTailIterable(negations_generator())
            if negations.tail.head is not None:
                yield from self._get_visitor(Intersection(negations), table)
            elif negations.head is not None:
                yield from self._get_visitor(negations.head, table)

    @_get_visitor.register
    def visit_intersection(self, exp: Intersection, table: SymbolsTable):
        if exp.head is not None:
            if exp.tail.head is None:
                yield from self._get_visitor(exp.head, table)
                return

            # cached_alts_generator = CachedGenerator(self._get_visitor)

            for head1, tail1, table in self._get_visitor(exp.head, table):
                for head2, tail2, table in self._get_visitor(exp.tail, table):
                    # `aA & bB = (a & b) + (A & B)`
                    tail = EMPTY_STRING if tail1 is tail2 is EMPTY_STRING \
                        else Intersection(tail1, tail2)
                    # `a & b = a`                 if `a == b`
                    head, table = table.intersect(head1, head2)
                    if head:
                        yield head, tail, table
                    # `a & b = {}`                if `a != b`

    @_get_visitor.register
    def visit_synchronization(self, exp: Synchronization, table: SymbolsTable):
        if exp.head is not None:
            if exp.tail.head is None:
                yield from self._get_visitor(exp.head, table)
                return

            # cached_alts_generator = CachedGenerator(alts_generator)

            for head1, tail1, table in self._get_visitor(exp.head, table):
                for head2, tail2, table in self._get_visitor(exp.tail, table):
                    # `aA @ bB = (a @ b) + (A @ B)`
                    tail = EMPTY_STRING if tail1 is tail2 is EMPTY_STRING \
                        else Synchronization(tail1, tail2)
                    # `a @ b = a`                     if `a == b`
                    head, table = table.intersect(head1, head2)
                    if head:
                        yield head, tail, table
                    # `a @ b = a // b`                if `a != b`
                    h1, t1, h2, t2 = table.difference(head1, head2)
                    if h1:
                        yield from self._get_visitor(Concatenation(Shuffle(h1, head2), tail), t1)
                    if h2:
                        yield from self._get_visitor(Concatenation(Shuffle(head1, h2), tail), t2)

    @_get_visitor.register
    def visit_concatenation(self, exp: Concatenation, table: SymbolsTable):
        if exp.head is not None:
            if exp.tail.head is None:
                yield from self._get_visitor(exp.head, table)
                return

            # if exp.head is EMPTY_STRING:
            #     yield exp.head, exp.tail, table
            # else:
            for head, tail, table in self._get_visitor(exp.head, table):
                tail = exp.tail if tail is EMPTY_STRING \
                    else Concatenation(tail, exp.tail)
                # if head is EMPTY_STRING:
                #     yield from alts_generator(tail, table)
                # else:
                yield head, tail, table

    @_get_visitor.register
    def visit_concatenation_repetition(self, exp: ConcatenationRepetition, table: SymbolsTable):
        assert exp.argument is not EMPTY_STRING, NOT_EMPTY_STRING_MESSAGE

        # a+1 = a
        if exp.lower_bound == exp.upper_bound == 1:
            return self._get_visitor(exp.argument, table)

        # a*n = empty | a*[1,n]
        elif exp.lower_bound == 0:
            return self._get_visitor(Union(EMPTY_STRING,
                                           ConcatenationRepetition(
                                               exp.argument,
                                               1, exp.upper_bound)),
                                     table)

        # a*[n,m] = a + a*[n-1,m-1] where n > 0
        else:
            return self._get_visitor(Concatenation.new(exp.argument,
                                                       ConcatenationRepetition(
                                                           exp.argument,
                                                           exp.lower_bound-1,
                                                           exp.upper_bound-1)),
                                     table)

    @_get_visitor.register
    def visit_shuffle(self, exp: Shuffle, table: SymbolsTable):
        if exp.head is not None:
            if exp.tail.head is None:
                yield from self._get_visitor(exp.head, table)
                return

            def shuffle(x, y, table):
                for head, tail, table in self._get_visitor(x, table):
                    # aA // B = a + (A // B) | ...
                    if tail is not EMPTY_STRING:
                        yield head, Shuffle(tail, y), table
                    else:
                        # a // B = a + B | ...
                        yield head, y, table

            yield from shuffle(exp.head, exp.tail, table)
            yield from shuffle(exp.tail, exp.head, table)

    @_get_visitor.register
    def visit_shuffle_repetition(self, exp: ShuffleRepetition, table: SymbolsTable):
        assert exp.argument is not EMPTY_STRING, NOT_EMPTY_STRING_MESSAGE

        # a//1 = a
        if exp.lower_bound == exp.upper_bound == 1:
            yield from self._get_visitor(exp.argument, table)

        # a%n = empty | a%[1,n]
        elif exp.lower_bound == 0:
            yield from self._get_visitor(Union(EMPTY_STRING,
                                               ShuffleRepetition(
                                                   exp.argument,
                                                   1, exp.upper_bound)),
                                         table)
        else:
            for head, tail, table in self._get_visitor(exp.argument, table):

                # (aB)%[n,m] = a*[n,m] if `B` is empty string
                if tail is EMPTY_STRING:
                    yield from self._get_visitor(exp.as_concatenation_repetition(), table)

                # = a + (B // aB%[n-1,m-1] ) where n > 0
                else:
                    yield head,\
                        Shuffle(tail,
                                ShuffleRepetition(
                                    exp.argument,
                                    exp.lower_bound-1,
                                    exp.upper_bound-1)), \
                        table

    @_get_visitor.register
    def visit_with_cached_wildcards(self, exp: WithCachedWildcards, table: SymbolsTable):
        for head, tail, table in self._get_visitor(exp.expression, table):
            number = exp.number
            if head is WILDCARD:
                head, table = table.get_wildcard(exp.cache_id, exp.number)
                number += 1

            if tail is not EMPTY_STRING:
                tail = WithCachedWildcards(tail, number, exp.cache_id)

            yield head, tail, table

    @_get_visitor.register
    def visit_substitution(self, exp: Substitution, table: SymbolsTable):
        assert exp is not EMPTY_STRING, NOT_EMPTY_STRING_MESSAGE

        def get_gen_alt(head, replacements):
            nonlocal exp_tail
            if exp_tail is not EMPTY_STRING:
                exp_tail = Substitution(exp_tail, replacements)

            return head, exp_tail, table

        for exp_head, exp_tail, table in self._get_visitor(exp.argument, table):
            if isinstance(exp_head, LettersPossitiveUnion):
                for exp_head in exp_head.letters:
                    # if there is nothing to replace
                    if (repl := exp.replacements.get(exp_head, exp_head)) is exp_head:
                        yield get_gen_alt(LettersPossitiveUnion({exp_head}), exp.replacements)
                    else:
                        if not isinstance(repl, (WithCachedWildcards, NamedWildcard)):
                            repl = WithCachedWildcards(repl, 0)
                        for repl_head, repl_tail, table in self._get_visitor(repl, table):
                            # a[D,a:r]     = r
                            # (aA)[D,a:r]  = r + A[D,a:r]
                            if repl_tail is EMPTY_STRING:
                                replacements = exp.replacements | {
                                    exp_head: repl_head}
                                yield get_gen_alt(repl_head, replacements)
                            else:
                                # a[D,a:rR] = r + R
                                if exp_tail is EMPTY_STRING:
                                    yield repl_head, repl_tail, table
                                # (aA)[D,a:rR] = r + R + A[D,a:rR]
                                # where `r` may be a cached previous NamedWildcard
                                else:
                                    replacements = exp.replacements | {
                                        exp_head: Concatenation(repl_head, repl_tail)}
                                    yield repl_head,\
                                        Concatenation(
                                            repl_tail,
                                            Substitution(exp_tail, replacements)),\
                                        table
            else:
                yield get_gen_alt(exp_head, exp.replacements)
