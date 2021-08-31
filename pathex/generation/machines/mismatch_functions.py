from operator import and_, or_, sub
from typing import Sequence

from pathex.expressions.nary_operators.union import Union
from pathex.expressions.terms.letters_complement import \
    LettersComplement
from pathex.expressions.terms.alphabet import Alphabet

from .machine import MachineMismatch

from pathex.expressions.terms.empty_word import EmptyWord

Mismatches = Sequence[tuple[object, object]]


def simple_mismatch(self: MachineMismatch, value1: object, value2: object) -> Mismatches:
    if value1 != value2:
        yield value1, value2


def _get_list_union(v1, v2, op, kind, second):
    s = op(v1)
    return [(kind(s), second)] if s else []


def general_mismatch_alphabet(value1: object, value2: object,
                                    type1, type2) -> Mismatches:
    if EmptyWord not in (type1, type2):
        if type1 == type2 == Alphabet:
            return []
        elif type1 == Alphabet:
            return [(LettersComplement({value2}), value2)]
        elif type2 == Alphabet:
            return [(LettersComplement({value1}), value1)]
    return []


def general_mismatch_completters(value1: object, value2: object,
                                       type1, type2) -> Mismatches:
    if EmptyWord not in (type1, type2):
        if type1 == type2 == LettersComplement:
            return (_get_list_union(value2.letters, value1.letters, sub, Union, value2) +
                    _get_list_union(value1.letters, value2.letters, sub, Union, value1))
        elif type1 == LettersComplement:
            return (_get_list_union(value1.letters, {value2}, or_, Union, value2) +
                    _get_list_union({value2}, value1.letters, and_, Union, value1))
        elif type2 == LettersComplement:
            return (_get_list_union({value1}, value2.letters, and_, Union, value2) +
                    _get_list_union({value2}, value1.letters, or_, Union, value1))
    return []


def general_mismatch_compalphabet(value1: object, value2: object,
                                                 type1, type2) -> Mismatches:
    if type1 == LettersComplement and type2 == Alphabet:
        return [(value1.letters, value1)]
    elif type1 == Alphabet and type2 == LettersComplement:
        return [(value2.letters, value2)]
    elif r := general_mismatch_alphabet(value1, value2, type1, type2):
        return r
    elif r := general_mismatch_completters(value1, value2, type1, type2):
        return r
    else:
        return []


def mismatch_with_(self: MachineMismatch,
                   value1: object, value2: object, func) -> Mismatches:
    type1, type2 = type(value1), type(value2)
    if mismatches := func(value1, value2, type1, type2):
        for mismatch, v in mismatches:
            if isinstance(mismatch, Union):
                yield from map(lambda x: (x, v), mismatch)
            else:
                yield mismatch, v
    else:
        yield from simple_mismatch(self, value1, value2)


def mismatch_alphabet(self: MachineMismatch,
                            value1: object, value2: object) -> Mismatches:
    return mismatch_with_(self, value1, value2, general_mismatch_alphabet)


def mismatch_completters(self: MachineMismatch,
                               value1: object, value2: object) -> Mismatches:
    return mismatch_with_(self, value1, value2, general_mismatch_completters)


def mismatch_compalphabet(self: MachineMismatch,
                                         value1: object, value2: object) -> Mismatches:
    return mismatch_with_(self, value1, value2, general_mismatch_compalphabet)
