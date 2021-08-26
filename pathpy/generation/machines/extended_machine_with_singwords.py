from .mismatch_functions import mismatch_with_singwords
from .match_functions import match_with_singwords
from .extended_machine import ExtendedMachine

__all__ = ['ExtendedMachineWithSingWords']

class ExtendedMachineWithSingWords(ExtendedMachine):
    match = match_with_singwords
    mismatch = mismatch_with_singwords
