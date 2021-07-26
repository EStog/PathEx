from __future__ import annotations
from itertools import islice, zip_longest

import threading
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from functools import wraps

from pathpy.expressions.nary_operators.concatenation import Concatenation
from pathpy.expressions.terms.letters_unions.letters_possitive_union import \
    LettersPossitiveUnion
from pathpy.generators._expressions._named_wildcard import NamedWildcard
from pathpy.generators.alternatives_generator import alts_generator
from pathpy.generators.symbols_table import SymbolsTable

__all__ = ['Synchronizer']


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

    >>> from concurrent.futures import ThreadPoolExecutor
    >>> from functools import partial
    >>> from pathpy import Synchronizer
    >>> from pathpy.generators.word_generator import WordGenerator

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

    >>> allowed_paths = exp.as_set_of_tuples()

    >>> assert tuple(shared_list) in allowed_paths
    """

    def __init__(self, exp, concurrency_type: ConcurrencyType = ConcurrencyType.THREADING):
        self._sync_module = concurrency_type.value
        self._labels = {}
        self._labels_lock = self._sync_module.Lock()
        self._alternatives = set()
        self._alternatives_lock = self._sync_module.Lock()
        self._alternatives.add((exp, SymbolsTable()))

    def wait_until_allowed(self, label):
        label = LettersPossitiveUnion({label})
        with self._labels_lock:
            lock = self._labels.setdefault(label, self._sync_module.Lock())
        lock.acquire()
        if new_alternatives := self._get_new_alternatives(label):
            lock.release()
            with self._alternatives_lock:
                self._alternatives = new_alternatives
            self._release_labels()
        else:
            lock.acquire()
            lock.release()

    def _get_new_alternatives(self, label):
        def _assert_right_match(label, match, table):
            if isinstance(match, NamedWildcard):
                match = table.get_value(match)
            else:  # isinstance(match, LettersPossitiveUnion):
                return LettersPossitiveUnion({match}) == label

        new_alternatives = set()
        with self._alternatives_lock:
            for exp, table in self._alternatives:
                for head, tail, table in alts_generator(exp, table):
                    match, table = table.intersect(head, label)
                    if match is not None:
                        assert _assert_right_match(label, match, table), \
                            f'Match is {match} instead of label "{label}"'
                        new_alternatives.add((tail, table))
        return new_alternatives

    def _release_labels(self):
        with self._labels_lock:
            for label in self._labels:
                if new_alternatives := self._get_new_alternatives(label):
                    lock = self._labels[label]
                    try:
                        lock.release()
                    except RuntimeError:
                        pass
                    else:
                        with self._alternatives_lock:
                            self._alternatives = new_alternatives

    def register(self, tag: _Tag, func=None):
        def wrapper(wrapped):
            @wraps(wrapped)
            def f(*args, **kwargs):
                self.wait_until_allowed(tag.enter)
                x = wrapped(*args, **kwargs)
                self.wait_until_allowed(tag.exit)
                return x
            return f

        if func is None:
            return wrapper
        else:
            return wrapper(func)

    @contextmanager
    def region(self, tag: _Tag):
        self.wait_until_allowed(tag.enter)
        try:
            yield self
        finally:
            self.wait_until_allowed(tag.exit)

    @classmethod
    def tags(cls, n: int, *names):
        return (_Tag(name=name) for _, name in islice(zip_longest(range(n), names), n))
