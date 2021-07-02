from __future__ import annotations

from functools import singledispatch
from math import inf
from typing import Generator

from pathpy.adts.cached_generators import CachedGenerator
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


@singledispatch
def alts_generator(expression: object, table: SymbolsTable) -> \
        Generator[tuple[Term, Expression, SymbolsTable], None, None]:
    yield LettersPossitiveUnion({expression}), EMPTY_STRING, table


@alts_generator.register
def visit_term(exp: Term, table: SymbolsTable):
    yield exp, EMPTY_STRING, table


@alts_generator.register
def visit_named_wildcard(exp: NamedWildcard, table: SymbolsTable):
    yield table.get_value(exp), EMPTY_STRING, table


@alts_generator.register
def visit_union(exp: Union, table: SymbolsTable):
    for e in exp:
        yield from alts_generator(e, table)


@alts_generator.register
def visit_negation(exp: Negation, table: SymbolsTable):
    argument_type = type(exp.argument)
    if argument_type is LettersPossitiveUnion:
        yield exp.argument.as_negative(), EMPTY_STRING, table
    elif argument_type is LettersNegativeUnion:
        yield exp.argument.as_possitive(), EMPTY_STRING, table
    elif exp.argument is EMPTY_STRING:
        yield from alts_generator(ConcatenationRepetition(WILDCARD, 1, inf), table)
    elif isinstance(exp.argument, NAryOperator):
        negations = []
        for head, tail, table in alts_generator(exp.argument, table):
            if tail:
                negations.append(Union(
                    Concatenation(Negation(head), Negation(tail)),
                    Concatenation(Negation(head), tail),
                    Concatenation(head, Negation(tail))))
            else:
                negations.append(Negation(head))
        if len(negations) > 1:
            yield from alts_generator(Intersection(negations), table)
        else:
            yield from alts_generator(negations[0], table)


@alts_generator.register
def visit_intersection(exp: Intersection, table: SymbolsTable):
    cached_alts_generator = CachedGenerator(alts_generator)

    for head1, tail1, table in alts_generator(exp.head, table):
        for head2, tail2, table in cached_alts_generator(exp.tail, table):
            # `aA & bB = (a & b) + (A & B)`
            tail = EMPTY_STRING if tail1 is tail2 is EMPTY_STRING \
                else Intersection(tail1, tail2)
            # `a & b = a`                 if `a == b`
            head, table = table.intersect(head1, head2)
            if head:
                yield head, tail, table
            # `a & b = {}`                if `a != b`


@alts_generator.register
def visit_synchronization(exp: Synchronization, table: SymbolsTable):
    cached_alts_generator = CachedGenerator(alts_generator)

    for head1, tail1, table in alts_generator(exp.head, table):
        for head2, tail2, table in cached_alts_generator(exp.tail, table):
            # `aA @ bB = (a @ b) + (A @ B)`
            tail = EMPTY_STRING if tail1 is tail2 is EMPTY_STRING \
                else Synchronization(tail1, tail2)
            # `a @ b = a`                     if `a == b`
            head, table = table.intersect(head1, head2)
            if head:
                yield head, tail, table
            # `a @ b = a // b`                if `a != b`
            else:
                yield from alts_generator(Concatenation(Shuffle(head1, head2), tail), table)


@alts_generator.register
def visit_concatenation(exp: Concatenation, table: SymbolsTable):
    if exp.head is EMPTY_STRING:
        yield from alts_generator(exp.tail, table)
    else:
        for head, tail, table in alts_generator(exp.head, table):
            tail = exp.tail if tail is EMPTY_STRING \
                else Concatenation(tail, exp.tail)
            if head is EMPTY_STRING:
                yield from alts_generator(tail, table)
            else:
                yield head, tail, table


@alts_generator.register
def visit_concatenation_repetition(exp: ConcatenationRepetition, table: SymbolsTable):
    assert exp.argument is not EMPTY_STRING, NOT_EMPTY_STRING_MESSAGE

    # a+1 = a
    if exp.lower_bound == exp.upper_bound == 1:
        return alts_generator(exp.argument, table)

    # a*n = empty | a*[1,n]
    elif exp.lower_bound == 0:
        return alts_generator(Union(EMPTY_STRING,
                                    ConcatenationRepetition(
                                        exp.argument,
                                        1, exp.upper_bound)),
                              table)

    # a*[n,m] = a + a*[n-1,m-1] where n > 0
    else:
        return alts_generator(Concatenation(exp.argument,
                                            ConcatenationRepetition(
                                                exp.argument,
                                                exp.lower_bound-1,
                                                exp.upper_bound-1)),
                              table)


@alts_generator.register
def visit_shuffle(exp: Shuffle, table: SymbolsTable):
    def shuffle(x, y, table):
        for head, tail, table in alts_generator(x, table):
            # aA // B = a + (A // B) | ...
            if tail is not EMPTY_STRING:
                yield head, Shuffle(tail, y), table
            else:
                # a // B = a + B | ...
                yield head, y, table

    yield from shuffle(exp.head, exp.tail, table)
    yield from shuffle(exp.tail, exp.head, table)


@alts_generator.register
def visit_shuffle_repetition(exp: ShuffleRepetition, table: SymbolsTable):
    assert exp.argument is not EMPTY_STRING, NOT_EMPTY_STRING_MESSAGE

    # a//1 = a
    if exp.lower_bound == exp.upper_bound == 1:
        yield from alts_generator(exp.argument, table)

    # a%n = empty | a%[1,n]
    elif exp.lower_bound == 0:
        yield from alts_generator(Union(EMPTY_STRING,
                                        ShuffleRepetition(
                                            exp.argument,
                                            1, exp.upper_bound)),
                                  table)
    else:
        for head, tail, table in alts_generator(exp.argument, table):

            # (aB)%[n,m] = a*[n,m] if `B` is empty string
            if tail is EMPTY_STRING:
                yield from alts_generator(exp.as_concatenation_repetition(), table)

            # = a + (B // aB%[n-1,m-1] ) where n > 0
            else:
                yield head,\
                    Shuffle(tail,
                            ShuffleRepetition(
                                exp.argument,
                                exp.lower_bound-1,
                                exp.upper_bound-1)), \
                    table


@alts_generator.register
def visit_with_cached_wildcards(exp: WithCachedWildcards, table: SymbolsTable):
    for head, tail, table in alts_generator(exp.expression, table):
        number = exp.number
        if head is WILDCARD:
            head, table = table.get_wildcard(exp.cache_id, exp.number)
            number += 1

        if tail is not EMPTY_STRING:
            tail = WithCachedWildcards(tail, number, exp.cache_id)

        yield head, tail, table


@alts_generator.register
def visit_substitution(exp: Substitution, table: SymbolsTable):
    assert exp is not EMPTY_STRING, NOT_EMPTY_STRING_MESSAGE

    def get_gen_alt(head, replacements):
        nonlocal exp_tail
        if exp_tail is not EMPTY_STRING:
            exp_tail = Substitution(exp_tail, replacements)

        return head, exp_tail, table

    for exp_head, exp_tail, table in alts_generator(exp.argument, table):
        if isinstance(exp_head, LettersPossitiveUnion):
            for exp_head in exp_head.letters:
                # if there is nothing to replace
                if (repl := exp.replacements.get(exp_head, exp_head)) is exp_head:
                    yield get_gen_alt(LettersPossitiveUnion({exp_head}), exp.replacements)
                else:
                    if not isinstance(repl, (WithCachedWildcards, NamedWildcard)):
                        repl = WithCachedWildcards(repl, 0)
                    for repl_head, repl_tail, table in alts_generator(repl, table):
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


__all__ = ['alternatives_generator']
