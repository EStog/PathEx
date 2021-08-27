from __future__ import annotations

from operator import or_, sub

from pathpy.expressions.nary_operators.union import Union
from pathpy.expressions.terms.letters_complement import \
    LettersComplement
from pathpy.expressions.terms.singleton_words import (SINGLETON_WORDS,
                                                      SingletonWords)
from pathpy.expressions.terms.empty_word import EmptyWord

from .machine import MachineWithMatch, Matches


def simple_match(self: MachineWithMatch, value1: object, value2: object) -> Matches:
    if value1 == value2:
        yield value1


def _get_union(v1, v2, op, kind):
    s = op(v1, v2)
    return kind(s) if s else None


def general_match_with_singwords(value1: object, value2: object,
                                 type1, type2) -> object:
    if EmptyWord not in (type1, type2):
        if type1 == type2 == SingletonWords:
            return SINGLETON_WORDS
        elif type1 == SingletonWords:
            return value2
        elif type2 == SingletonWords:
            return value1


def general_match_with_complemented(value1: object, value2: object,
                                    type1, type2) -> object:
    if EmptyWord not in (type1, type2):
        if type1 == type2 == LettersComplement:
            # De Morgan's Law
            return _get_union(value1.letters, value2.letters, or_, LettersComplement)
        elif type1 == LettersComplement:
            return _get_union({value2}, value1.letters, sub, Union)
        elif type2 == LettersComplement:
            return _get_union({value1}, value2.letters, sub, Union)


def general_match_with_complemented_singwords(value1: object, value2: object,
                                              type1, type2) -> object:
    if type1 == LettersComplement and type2 == SingletonWords:
        return value1
    elif type1 == SingletonWords and type2 == LettersComplement:
        return value2
    elif match := general_match_with_singwords(value1, value2, type1, type2):
        return match
    elif match := general_match_with_complemented(value1, value2, type1, type2):
        return match


def match_with_(self: MachineWithMatch, value1: object, value2: object, func) -> Matches:
    type1, type2 = type(value1), type(value2)
    if match := func(value1, value2, type1, type2):
        if isinstance(match, Union):
            yield from match
        else:
            yield match
    else:
        yield from simple_match(self, value1, value2)


def match_with_singwords(self: MachineWithMatch,
                         value1: object, value2: object) -> Matches:
    return match_with_(self, value1, value2,
                       general_match_with_singwords)


def match_with_complemented(self: MachineWithMatch,
                            value1: object, value2: object) -> Matches:
    return match_with_(self, value1, value2,
                       general_match_with_complemented)


def match_with_complemented_singwords(self: MachineWithMatch,
                                      value1: object, value2: object) -> Matches:
    return match_with_(self, value1, value2,
                       general_match_with_complemented_singwords)
