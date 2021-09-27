"""
Example using :meth:`process_register`
"""

import os
import os.path
import sys
from multiprocessing.managers import SyncManager

# this line is necessary if pathex is not installed and the program will be runned from the main folder of the project.
sys.path.append(os.getcwd())

from pathex import (ProcessPoolExecutor, Tag, process_register,
                    process_manager)
from pathex.adts.util import SET_OF_TUPLES

# Tags must be named and visible for import
a, b, c = Tag.named("a", "b", "c")


@process_register(a)
def func_a(shared_list):
    shared_list.append(a.enter)
    # print("Func a")
    shared_list.append(a.exit)


@process_register(b)
def func_b(shared_list):
    shared_list.append(b.enter)
    # print("Func b")
    shared_list.append(b.exit)


@process_register(c)
def func_c(shared_list):
    shared_list.append(c.enter)
    # print("Func c")
    shared_list.append(c.exit)


if __name__ == "__main__":
    print('testing ``process_register``...')

    # logger = multiprocessing.log_to_stderr()
    # logger.setLevel(logging.INFO)

    exp = (a + (b | c)) + 2

    psync = process_manager(exp, manager_class=SyncManager)

    shared = psync.list()

    with ProcessPoolExecutor(psync.address, max_workers=4) as executor:
        r1 = executor.submit(func_c, shared)
        r2 = executor.submit(func_a, shared)
        r3 = executor.submit(func_b, shared)
        r4 = executor.submit(func_a, shared)

        # r1.result(), r2.result(), r3.result(), r4.result()

    allowed_paths = exp.get_language(SET_OF_TUPLES)
    assert tuple(shared) in allowed_paths
