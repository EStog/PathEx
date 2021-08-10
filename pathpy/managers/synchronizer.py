from __future__ import annotations

import threading
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from itertools import islice, zip_longest

from pathpy.adts.multitask.acquired_lock import AcquiredLock
from pathpy.expressions.nary_operators.concatenation import Concatenation
from pathpy.expressions.terms.letters_unions.letters_possitive_union import \
    LettersPossitiveUnion
from pathpy.generators._expressions._named_wildcard import NamedWildcard
from pathpy.generators.alternatives_generator import AlternativesGenerator
from pathpy.generators.symbols_table import SymbolsTable

__all__ = ['Synchronizer']

# TODO: refactor by using Shuffle and Intersection, and generalize to any kind of synchronizer

class ConcurrencyType(Enum):
    THREADING = threading


@dataclass(frozen=True, init=False, eq=False)
class _Label:
    parent: _Tag

    def __repr__(self) -> str:
        if hasattr(self.parent, 'name'):
            return f'{self.__class__.__name__[1:]}({self.parent.name})'
        else:
            return f'{self.__class__.__name__[1:]}({id(self.parent)})'

    def __hash__(self) -> int:
        return id(self)


class _Enter(_Label):
    pass


class _Exit(_Label):
    pass


@dataclass(frozen=True, init=False, eq=False)
class _Tag(Concatenation):

    enter: _Label
    exit: _Label

    def __new__(cls, *args, name=None):
        if args:
            return super().__new__(cls, *args)
        enter = _Enter()
        exit = _Exit()
        self = super().__new__(cls, enter, exit)

        if name is not None:
            object.__setattr__(self, 'name', name)

        object.__setattr__(enter, 'parent', self)
        object.__setattr__(exit, 'parent', self)
        object.__setattr__(self, 'enter', enter)
        object.__setattr__(self, 'exit', exit)
        return self

    def __repr__(self) -> str:
        if hasattr(self, 'name'):
            return f'{self.__class__.__name__[1:]}({self.name})'
        else:
            return f'{self.__class__.__name__[1:]}({id(self)})'

    def __hash__(self) -> int:
        return id(hash)


class Synchronizer:
    """This class is a manager that controls the execution of its registered threads.
    """

    def __init__(self, exp, concurrency_type: ConcurrencyType = ConcurrencyType.THREADING):
        self._sync_module = concurrency_type.value
        self._sync_lock = self._sync_module.Lock()
        self._labels: dict[object, AcquiredLock] = {}
        self._alternatives = set()
        self._alternatives.add((exp, SymbolsTable()))

    def check(self, label: object):
        """This method is used to wait for the availability of a single label.

        The label may be any comparable object. If the expression of the synchronizer is not able to generate the given object then the execution is blocked until the presence of another label in another task advances the associated expression's automata, so it can generate the label given in this method.

        The direct use of this method should be exercised with caution, because it leads to non structured code. In fact, in an object oriented design, its use should be discouraged. This method is public just because it might be usefull in a very specific and extraordinary use case where an structured approach may be too expensive, harder to design or to maintain.

        For an structured approach use the decorator `Synchronizer.register` or the context manager `Synchronizer.region`.

        Example:

            >>> from concurrent.futures import ThreadPoolExecutor
            >>> from pathpy import Synchronizer, Concatenation as C

            The following expression generates 'PiPfCiCf' | 'PiPfCiCfPiPfCiCf' | ...
            >>> exp = +C('Pi','Pf','Ci','Cf')
            >>> sync = Synchronizer(exp)
            >>> produced = []
            >>> consumed = []

            >>> def producer(x):
            ...     sync.check('Pi')
            ...     produced.append(x)
            ...     sync.check('Pf')

            >>> def consumer():
            ...     sync.check('Ci')
            ...     consumed.append(produced.pop())
            ...     sync.check('Cf')

            >>> with ThreadPoolExecutor(max_workers=8) as executor:
            ...     for _ in range(4):
            ...         _ = executor.submit(consumer)
            ...     for i in range(4):
            ...         _ = executor.submit(producer, i)

            >>> assert produced == []
            >>> assert consumed == [0, 1, 2, 3]

        Args:
            label (object): The label to wait for.
        """
        label = LettersPossitiveUnion({label})

        self._sync_lock.acquire()  # protect the entire procedure

        if new_alternatives := self._get_new_alternatives(label):
            self._alternatives = new_alternatives
            self._check_saved_labels()
            self._sync_lock.release()
        else:
            lock = self._labels.setdefault(
                label, AcquiredLock(self._sync_module.Lock))

            # release the procedure's protection lock in order to get blocked in the following line, so the blocking will be because this task being waiting for some other task, not because of the procedure's protection lock
            self._sync_lock.release()

            # lock.acquire in order to block.
            # lock.release must be done by another task.
            lock.acquire()

    def _check_saved_labels(self):
        while True:
            for label in self._labels:
                lock = self._labels[label]
                if lock.waiting_amount > 0:
                    if new_alternatives := self._get_new_alternatives(label):
                        lock.release()
                        self._alternatives = new_alternatives
                        break
            else:
                break

    def _get_new_alternatives(self, label):
        def _assert_right_match(label, match, table):
            if isinstance(match, NamedWildcard):
                return match == table.get_value(match)
            elif isinstance(match, LettersPossitiveUnion):
                return match == label
            else:
                return False

        new_alternatives = set()
        for exp, table in self._alternatives:
            for head, tail, table in AlternativesGenerator(exp, table, not_normal=True):
                match, table = table.intersect(head, label)
                if match is not None:
                    assert _assert_right_match(label, match, table), \
                        f'Match is {match} instead of label "{label}"'
                    new_alternatives.add((tail, table))
        return new_alternatives

    def register(self, tag: _Tag, func=None):
        """
        >>> from concurrent.futures import ThreadPoolExecutor
        >>> from pathpy import Synchronizer

        >>> a, b, c = Synchronizer.tags(3)

        >>> exp = ( a + (b|c) )+2

        >>> shared_list = []

        >>> sync = Synchronizer(exp)

        >>> @sync.register(a)
        ... def func_a():
        ...     shared_list.append(a.enter)
        ...     # print('Func a')
        ...     shared_list.append(a.exit)

        >>> @sync.register(b)
        ... def func_b():
        ...     shared_list.append(b.enter)
        ...     # print('Func b')
        ...     shared_list.append(b.exit)

        >>> @sync.register(c)
        ... def func_c():
        ...     shared_list.append(c.enter)
        ...     # print('Func c')
        ...     shared_list.append(c.exit)

        >>> with ThreadPoolExecutor(max_workers=4) as executor:
        ...     _ = executor.submit(func_c)
        ...     _ = executor.submit(func_a)
        ...     _ = executor.submit(func_b)
        ...     _ = executor.submit(func_a)

        >>> from pathpy.adts.collection_wrapper import get_collection_wrapper
        >>> Set = get_collection_wrapper(set, lambda s, w: s.add(tuple(w)))
        >>> allowed_paths = exp.get_language(Set)

        >>> assert tuple(shared_list) in allowed_paths
        """
        def wrapper(wrapped):
            @wraps(wrapped)
            def f(*args, **kwargs):
                self.check(tag.enter)
                x = wrapped(*args, **kwargs)
                self.check(tag.exit)
                return x
            return f

        if func is None:
            return wrapper
        else:
            return wrapper(func)

    @contextmanager
    def region(self, tag: _Tag):
        self.check(tag.enter)
        try:
            yield self
        finally:
            self.check(tag.exit)

    @classmethod
    def tags(cls, n: int, *names):
        return (_Tag(name=name) for _, name in islice(zip_longest(range(n), names), n))
