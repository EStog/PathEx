"""
Example using :meth:`register`
"""
import os
import os.path
import sys
sys.path.append(os.getcwd())

from multiprocessing.managers import SyncManager

from pathpy import (ProcessPoolExecutor, Tag, process_register,
                    process_synchronizer)
from pathpy.adts.util import SET_OF_TUPLES

a, b, c = Tag.named('a', 'b', 'c')


@process_register(a)
def func_a(shared_list):
    shared_list.append(a.enter)
    print('Func a')
    shared_list.append(a.exit)


@process_register(b)
def func_b(shared_list):
    shared_list.append(b.enter)
    print('Func b')
    shared_list.append(b.exit)


@process_register(c)
def func_c(shared_list):
    shared_list.append(c.enter)
    print('Func c')
    shared_list.append(c.exit)


if __name__ == '__main__':
    # logger = multiprocessing.log_to_stderr()
    # logger.setLevel(logging.INFO)

    exp = (a + (b | c))+2

    pmanager = process_synchronizer(
        exp, manager_class=SyncManager)

    shared = pmanager.list()

    with ProcessPoolExecutor(pmanager.address, max_workers=4) as executor:
        r1 = executor.submit(func_c, shared)
        r2 = executor.submit(func_a, shared)
        r3 = executor.submit(func_b, shared)
        r4 = executor.submit(func_a, shared)

        # r1.result(), r2.result(), r3.result(), r4.result()

    allowed_paths = exp.get_language(SET_OF_TUPLES)
    assert tuple(shared) in allowed_paths
