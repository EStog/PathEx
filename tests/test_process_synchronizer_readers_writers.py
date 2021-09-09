"""
Example of *readers* and *writers* processes
"""

# XXX: DO NOT AUTOMATICALLY FORMAT THIS FILE!

import os
import sys
from multiprocessing.managers import SyncManager

# this line is necessary if pathex is not installed and the program will be runned from the main folder of the project.
sys.path.append(os.getcwd())

from pathex import (ProcessPoolExecutor, Tag, process_register,
                    process_synchronizer)

# Tags must be named and visible for import
writer, reader = Tag.named('writer', 'reader')


@process_register(writer)
def append(shared_buffer, x):
    shared_buffer.append(x)


@process_register(reader)
def get_top(shared_buffer):
    try:
        x = shared_buffer[0]
    except Exception:
        return None
    else:
        return x


@process_register(writer)
def appendleft(shared_buffer, x):
    shared_buffer.insert(0, x)


if __name__ == '__main__':

    exp = (writer | reader//...)+...

    psync = process_synchronizer(
        exp, manager_class=SyncManager)

    shared_buffer = psync.list()

    with ProcessPoolExecutor(psync.address, max_workers=4) as executor:
        _ = [executor.submit(append, shared_buffer, 4) for _ in range(5)]
        _ = [executor.submit(get_top, shared_buffer) for _ in range(5)]
        _ = [executor.submit(appendleft, shared_buffer, 3) for _ in range(5)]

    assert list(shared_buffer) == [3, 3, 3, 3, 3, 4, 4, 4, 4, 4]
