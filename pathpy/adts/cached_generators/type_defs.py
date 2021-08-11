from __future__ import annotations

from typing import Callable, Collection, Iterator, Protocol, TypeVar
from typing import Union as TUnion

__all__ = ['TDecorableGenerator',
           'TDecorableDescriptorGenerator', 'TCacheType']

_E = TypeVar('_E')
_E_co = TypeVar('_E_co', covariant=True)

TDecorableGenerator = Callable[..., Iterator[_E]]

TCacheType = dict[
    tuple,
    tuple[TUnion[Collection[_E]],
          Iterator[_E]]
]


class TDecorableDescriptorGenerator(Protocol[_E_co]):
    def __get__(self, obj, cls=None) -> TDecorableGenerator[_E_co]: ...
    def __call__(self, *args, **kwargs) -> Iterator[_E_co]: ...
