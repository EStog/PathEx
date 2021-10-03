"""
Example of *readers* and *writers* processes
"""

import concurrent.futures as cf
import os
import sys
from multiprocessing.managers import SyncManager

# this line is necessary if pathex is not installed and the program will be runned from the main folder of the project.
sys.path.append(os.getcwd())  # noqa

from pathex import ProcessPoolExecutor, Tag, process_manager, process_register

# Tags must be named and visible for import
writer, reader = Tag.named("writer", "reader")


@process_register(writer)
def append(shared_buffer, x):
    shared_buffer.append(x)


@process_register(reader)
def get_len(shared_buffer):
    return len(shared_buffer)


@process_register(writer)
def appendleft(shared_buffer, x):
    shared_buffer.insert(0, x)


if __name__ == "__main__":

    print('testing ``process_register`` with readers-writers...')

    exp = (writer | reader//...)+...

    psync = process_manager(exp, manager_class=SyncManager)

    shared_buffer = psync.list()

    tasks = []

    with ProcessPoolExecutor(psync.address, max_workers=4) as executor:
        tasks.extend([executor.submit(get_len, shared_buffer) for _ in range(5)])
        tasks.extend([executor.submit(append, shared_buffer, 4) for _ in range(5)])
        tasks.extend([executor.submit(appendleft, shared_buffer, 3) for _ in range(5)])

        done, not_done = cf.wait(tasks, timeout=None, return_when=cf.ALL_COMPLETED)
        assert not not_done

    assert list(shared_buffer) == [3, 3, 3, 3, 3, 4, 4, 4, 4, 4]
