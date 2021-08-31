from pathex.generation.machines.match_functions import match_compalphabet
from pathex.generation.machines.mismatch_functions import \
    mismatch_compalphabet

from .extended_machine_alphabet import ExtendedMachineAlphabet

__all__ = ['ExtendedMachineCompalphabet']


class ExtendedMachineCompalphabet(ExtendedMachineAlphabet):
    match = match_compalphabet
    mismatch = mismatch_compalphabet
