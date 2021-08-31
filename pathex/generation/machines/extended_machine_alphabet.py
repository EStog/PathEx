from .mismatch_functions import mismatch_alphabet
from .match_functions import match_alphabet
from .extended_machine import ExtendedMachine

__all__ = ['ExtendedMachineAlphabet']

class ExtendedMachineAlphabet(ExtendedMachine):
    match = match_alphabet
    mismatch = mismatch_alphabet
