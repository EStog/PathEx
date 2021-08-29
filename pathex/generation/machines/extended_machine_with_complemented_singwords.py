from pathex.generation.machines.match_functions import \
    match_with_complemented_singwords
from pathex.generation.machines.mismatch_functions import \
    mismatch_with_complemented_singwords

from .extended_machine_with_singwords import ExtendedMachineWithSingWords

__all__ = ['ExtendedMachineWithComplementedSingWords']


class ExtendedMachineWithComplementedSingWords(ExtendedMachineWithSingWords):
    match = match_with_complemented_singwords
    mismatch = mismatch_with_complemented_singwords
