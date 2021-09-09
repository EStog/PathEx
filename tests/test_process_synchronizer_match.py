"""
Example using :meth:`match`:
"""

#XXX: DO NOT AUTOMATICALLY FORMAT THIS FILE!

import os
import os.path
import sys
from concurrent.futures import ProcessPoolExecutor
from multiprocessing.managers import SyncManager

# this line is necessary if pathex is not installed and the program will be runned from the main folder of the project.
sys.path.append(os.getcwd())

from pathex.expressions.aliases import *
from pathex.managing.process_synchronizer import (get_synchronizer,
                                                  process_synchronizer)


def producer(address, produced, x):
    sync = get_synchronizer(address)
    sync.match('Pi')
    produced.append(x)
    sync.match('Pf')


def consumer(address, produced, consumed):
    sync = get_synchronizer(address)
    sync.match('Ci')
    consumed.append(produced.pop())
    sync.match('Cf')


if __name__ == '__main__':
    # The following expression generates 'PiPfCiCf' | 'PiPfCiCfPiPfCiCf' | ...
    exp = +C('Pi', 'Pf', 'Ci', 'Cf')
    psync = process_synchronizer(exp, manager_class=SyncManager)
    produced = psync.list()
    consumed = psync.list()

    with ProcessPoolExecutor(max_workers=8) as executor:
        for _ in range(4):
            executor.submit(consumer, psync.address, produced, consumed)
        for i in range(4):
            executor.submit(producer, psync.address, produced, i)

    assert list(produced) == []
    assert set(consumed) == {0, 1, 2, 3}
    sync = get_synchronizer(psync.address)
    assert sync.requests('Pi') == sync.permits(
        'Pf') == sync.requests('Ci') == sync.permits('Cf') == 4
