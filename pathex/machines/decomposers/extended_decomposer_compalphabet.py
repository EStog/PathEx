from pathex.machines.decomposers.extended_decomposer_alphabet import \
    ExtendedDecomposerAlphabet
from pathex.machines.decomposers.match_functions import match_compalphabet
from pathex.machines.decomposers.mismatch_functions import \
    mismatch_compalphabet

__all__ = ['ExtendedDecomposerCompalphabet']


class ExtendedDecomposerCompalphabet(ExtendedDecomposerAlphabet):
    match = match_compalphabet
    mismatch = mismatch_compalphabet
