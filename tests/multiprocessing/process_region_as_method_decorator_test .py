"""
Example using :meth:`region` as method decorator for processes
"""

import concurrent.futures as cf
import os
import sys

# this line is necessary if pathex is not installed and the program will be runned from the main folder of the project.
sys.path.append(os.getcwd())  # noqa

from pathex import Tag, get_synchronizer
from pathex.adts.util import SET_OF_TUPLES

class SharedList:

    # Tags must be named and visible for import
    a, b, c = Tag.named("a", "b", "c")
    exp = (a + (b | c)) + 2
    sync = get_synchronizer(exp, module_name=__name__)

    def __init__(self):
        self._list = self.sync.get_mp_manager().list()

    def __iter__(self):
        return iter(self._list)

    @sync.region(a)
    def func_a(self):
        self._list.append(self.a.enter)
        print("Func a")
        self._list.append(self.a.exit)


    @sync.region(b)
    def func_b(self):
        self._list.append(self.b.enter)
        print("Func b")
        self._list.append(self.b.exit)


    def func_c(self):
        self._list.append(self.c.enter)
        print("Func c")
        self._list.append(self.c.exit)


    func_c = sync.region(c)(func_c)


if __name__ == "__main__":
    print('testing ``process_register``...')

    # logger = multiprocessing.log_to_stderr()
    # logger.setLevel(logging.INFO)

    tasks = []

    shared = SharedList()

    with cf.ProcessPoolExecutor(max_workers=4) as executor:
        tasks.append(executor.submit(shared.func_c))
        tasks.append(executor.submit(shared.func_a))
        tasks.append(executor.submit(shared.func_b))
        tasks.append(executor.submit(shared.func_a))

        done, not_done = cf.wait(tasks, timeout=None, return_when=cf.ALL_COMPLETED)
        assert not not_done

    allowed_paths = shared.exp.get_language(SET_OF_TUPLES)
    assert tuple(shared) in allowed_paths
    print("All right!")
