from pathex.machines.decomposers.extended_decomposer import ExtendedDecomposer
from pathex.machines.decomposers.match_functions import match_alphabet
from pathex.machines.decomposers.mismatch_functions import mismatch_alphabet

__all__ = ['ExtendedDecomposerAlphabet']


class ExtendedDecomposerAlphabet(ExtendedDecomposer):
    match = match_alphabet
    mismatch = mismatch_alphabet
