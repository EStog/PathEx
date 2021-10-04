"""
Example using :meth:`process_register`
"""

import concurrent.futures as cf
import os
import os.path
import sys
from multiprocessing.managers import SyncManager

# this line is necessary if pathex is not installed and the program will be runned from the main folder of the project.
sys.path.append(os.getcwd())  # noqa

from pathex import ProcessPoolExecutor, Tag, process_manager, process_register
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


def func_c(shared_list):
    shared_list.append(c.enter)
    # print("Func c")
    shared_list.append(c.exit)


func_c = process_register(c, func_c)


if __name__ == "__main__":
    print('testing ``process_register``...')

    # logger = multiprocessing.log_to_stderr()
    # logger.setLevel(logging.INFO)

    exp = (a + (b | c)) + 2

    psync = process_manager(exp, manager_class=SyncManager)

    shared = psync.list()

    tasks = []

    with ProcessPoolExecutor(psync.address, max_workers=4) as executor:
        tasks.append(executor.submit(func_c, shared))
        tasks.append(executor.submit(func_a, shared))
        tasks.append(executor.submit(func_b, shared))
        tasks.append(executor.submit(func_a, shared))

        done, not_done = cf.wait(tasks, timeout=None, return_when=cf.ALL_COMPLETED)
        assert not not_done

    allowed_paths = exp.get_language(SET_OF_TUPLES)
    assert tuple(shared) in allowed_paths
