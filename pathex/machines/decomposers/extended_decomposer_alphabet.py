from .extended_decomposer import ExtendedDecomposer
from .match_functions import match_alphabet
from .mismatch_functions import mismatch_alphabet

__all__ = ['ExtendedDecomposerAlphabet']


class ExtendedDecomposerAlphabet(ExtendedDecomposer):
    match = match_alphabet
    mismatch = mismatch_alphabet
