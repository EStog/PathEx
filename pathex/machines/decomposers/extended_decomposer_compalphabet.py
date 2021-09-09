from .extended_decomposer_alphabet import ExtendedDecomposerAlphabet
from .match_functions import match_compalphabet
from .mismatch_functions import mismatch_compalphabet

__all__ = ['ExtendedDecomposerCompalphabet']


class ExtendedDecomposerCompalphabet(ExtendedDecomposerAlphabet):
    match = match_compalphabet
    mismatch = mismatch_compalphabet
