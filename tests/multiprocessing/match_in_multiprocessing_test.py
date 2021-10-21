"""
Example using :meth:`match`:
"""

import concurrent.futures as cf
import os
import sys

# this line is necessary if pathex is not installed and the program will be runned from the main folder of the project.
sys.path.append(os.getcwd())  # noqa

from pathex import get_synchronizer
from pathex.expressions.aliases import *

exp = +C("Pi", "Pf", "Ci", "Cf")
sync = get_synchronizer(exp, module_name=__name__)


def producer(produced, x):
    sync.match("Pi")
    produced.append(x)
    print(f'Produced {x}')
    print(f'produced={produced}')
    sync.match("Pf")


def consumer(produced, consumed):
    sync.match("Ci")
    x = produced.pop()
    consumed.append(x)
    print(f'consumed {x}')
    print(f'produced={produced}')
    print(f'consumed={consumed}')
    sync.match("Cf")


if __name__ == "__main__":
    print('testing ``Synchronizer.match`` in multiprocessing...')

    # The following expression generates 'PiPfCiCf' | 'PiPfCiCfPiPfCiCf' | ...

    manager = sync.get_mp_manager()
    produced = manager.list()
    consumed = manager.list()

    tasks = []

    with cf.ProcessPoolExecutor(max_workers=8) as executor:
        for _ in range(4):
            tasks.append(executor.submit(consumer, produced, consumed))
        for i in range(4):
            tasks.append(executor.submit(producer, produced, i))

        done, not_done = cf.wait(tasks, timeout=None, return_when=cf.ALL_COMPLETED)
        assert not not_done

    assert list(produced) == []
    assert set(consumed) == {0, 1, 2, 3}
    assert (
        sync.requests("Pi")
        == sync.permits("Pf")
        == sync.requests("Ci")
        == sync.permits("Cf")
        == 4
    )

    print('All right!')
