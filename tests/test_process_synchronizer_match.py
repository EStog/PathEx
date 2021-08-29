"""
Example using :meth:`match`:
"""
import os
import os.path
import sys
sys.path.append(os.getcwd())

from concurrent.futures import ProcessPoolExecutor
from multiprocessing.managers import SyncManager

from pathex import Concatenation as C
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
    exp = +C('Pi','Pf','Ci','Cf')
    pmanager = process_synchronizer(exp, manager_class=SyncManager)
    produced = pmanager.list()
    consumed = pmanager.list()

    with ProcessPoolExecutor(max_workers=8) as executor:
        for _ in range(4):
           executor.submit(consumer, pmanager.address, produced, consumed)
        for i in range(4):
            executor.submit(producer, pmanager.address, produced, i)

    assert list(produced) == []
    assert set(consumed) == {0, 1, 2, 3}
    sync = get_synchronizer(pmanager.address)
    assert sync.requests('Pi') == sync.permits('Pf') == sync.requests('Ci') == sync.permits('Cf') == 4
