import functools as _fts
import inspect as _insp
import itertools as _its
import typing as _t
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType
from warnings import warn as _warn

_T_co = _t.TypeVar('_T_co', covariant=True)


def same(x): return x, None
def ignore(x): return _t.Any, None
def get_type(x): return type(x), None


def _default_first(x): return None, None


@_dataclass(frozen=True)
class ValuesUnion:
    """This is a general union.
    It allows unions inside an union, but it does not flatten.
    This allows to consider ValuesUnion itself as a value.
    """
    args: tuple

    def __init__(self, *args):
        object.__setattr__(self, 'args', args)


class MultifunctionByEquality(_t.Generic[_T_co]):
    """This is a decorator for turning a function into a multifunction
    that dispatch taking into account the equality of some property
    of the arguments to a given value. It is a functional realization
    of `case of`-like instructions.

    This decorator can handle multiple dispatch and might be preferred to
    `functools.singledispatch` when there is not hierarchy in the types of
    the arguments. Like `functools.singledispatch` it provides `register`,
    `dispatch` and `registry` attributes.

    Two keywords only arguments are possible:
        `properties`: to specify each property of each parameter.
            The length of `properties` might be of any length. Each property is a function that takes an argument and  returns a two-elements tuple. The first element is the value to be matched, the second is a surplus to be passed to the function in its variable positional argument.
            Arguments to be ignored must be explicitly specified as `ignore`. Arguments which values are to be taken identically as they are may be specified as `same`.
            Defaults to `()`.
        `default`: the default property in case a parameter has no specified property and it is not annotated. If the parameter is annotated, the annotation is used instead.
            Defaults to `type`.

    The resulting object has a `register` decorator method with two keywords
    only parameters:
        `values`: the values to be matched in order to choose the decorated
            function. If the corresponding property for a parameter is `ignore`
            then the value must be `typing.Any` or not specified.
            Defaults to `()`.
        `default`: the default value in case a parameter has no specified
            value and it is not annotated. If the parameter is annotated,
            the annotation is used instead.
            Defaults to `typing.Any`.

    Like `functools.singledispatch` can be stacked several times in order to
    register different values, but a warning will be issued if `register` is
    called more than once for the same sequence of values. Also, different kind
    of unions can be used to specified different alternatives in a more concise
    manner.

    Examples:

    >>> @MultifunctionByEquality
    ... def f(a, b, c):
    ...     return f'Default function: {a}, {b}, {c}'

    >>> @f.register(default=int)
    ... def _(a, b, c):
    ...     return f'int, int, int: {a}, {b}, {c}'

    >>> assert f(3, 4, 5) == 'int, int, int: 3, 4, 5'
    >>> assert f('e', 'a', 4) == 'Default function: e, a, 4'

    `typing.Union` is recognized as a way of specifying different matching
    alternatives. Also a different class `ValuesUnion` is provided that can
    be used in contexts different from types and it does not flatten, which
    allows to use `ValuesUnion` itself as a value.

    Special object `Union` may be used to specify different alternatives for the
    function. `typing.Union` is recognized as well, but that last one can only be
    used with types and it flattens the union of unions. The `Union` defined in this
    module may be used in any context and it does not flatten, which allows to use
    `Union` itself as a value.

    >>> import typing as _t

    >>> @f.register
    ... def fff(a: str, b: dict[int, int], c: _t.Union[int, dict[str, str]]):
    ...     return 'The third option'

    >>> assert f.dispatch(str, dict, int) is fff
    >>> assert f.dispatch(str, dict, dict) is fff
    >>> assert f('s', {3:4}, {'w':'r'}) == 'The third option'
    >>> assert f('s', {3:4}, {'w':3}) == 'The third option'
    >>> assert f('s', {3:4}, 3) == 'The third option'

    >>> @f.register
    ... def _(a: str, b: int):
    ...     return f'str, int: {a}, {b}'
    >>> assert f('a', 4) == 'str, int: a, 4'

    >>> @MultifunctionByEquality(default=same)
    ... def g(a: ignore, b, c):
    ...     return f'Default function: {a}, {b}, {c}'

    >>> @g.register
    ... def _(a, b: 3, c: 4):
    ...     return 'b, c == 3, 4'

    >>> assert g(1, 2, 3) == 'Default function: 1, 2, 3'
    >>> assert g(1, 3, 4) == 'b, c == 3, 4'

    >>> @g.register
    ... def _(a, b: ValuesUnion(5, 6), c:7):
    ...    return 'The last one'

    >>> assert g(3, 5, 7) == 'The last one'
    >>> assert g(4, 6, 7) == 'The last one'
    >>> assert g(4, 6, 8) == 'Default function: 4, 6, 8'

    Length of `values` must be less or equal to the amount of parameters
    of the decorated function.

    >>> try:
    ...     @g.register(values=[_t.Any, 3, 4, 5])
    ...     def _(a, b, c):
    ...         return 'b, c == 3, 4'
    ... except AssertionError:
    ...     pass # Right!
    ... else:
    ...     print('Wrong!')
    """

    def __init__(
        self, func: _t.Optional[_t.Callable[..., _T_co]] = None,
        properties: _t.Sequence[_t.Callable[[_t.Any],
                                            tuple[_t.Hashable, _t.Any]]] = (),
        default: _t.Callable[[_t.Any], tuple[_t.Hashable, _t.Any]] = get_type
    ) -> None:
        assert isinstance(properties, _t.Sequence), \
            '`properties` argument must be Sequence'
        assert isinstance(default, _t.Callable), \
            'Default must be callable'
        self._default = default
        self._properties = properties
        self._table: dict[tuple[object, ...], _t.Callable[..., _T_co]] = {}
        self.__wrapped__ = func
        if func is None:
            self._call = self._complete
        else:
            self._call = self._redirect
            self._complete(func)

    def __call__(self, *args):
        return self._call(*args)

    def _complete(self, func: _t.Callable[..., _T_co]) -> 'MultifunctionByEquality[_T_co]':
        self.__wrapped__ = func
        assert isinstance(func, _t.Callable), \
            'Decorated object must be callable'
        func_parameters, args_name = self._get_parameters(func)
        annotated = self._get_annotated(func, args_name)
        if not self._properties:
            self._properties = [self._default if p.name not in annotated else annotated[p.name]
                                for p in func_parameters]
        _fts.update_wrapper(wrapped=func, wrapper=self)
        self._call = self._redirect
        return self

    def _get_parameters(self, func):
        func_parameters = tuple(_insp.signature(func).parameters.values())
        assert all(p.kind not in (_insp.Parameter.KEYWORD_ONLY, _insp.Parameter.VAR_KEYWORD)
                   for p in func_parameters), 'Arguments can not be keyword only'
        args_name = '' if func_parameters[-1].kind != _insp.Parameter.VAR_POSITIONAL \
            else func_parameters[-1].name
        if args_name:
            func_parameters = func_parameters[:-1]
        assert len(
            func_parameters) > 0, 'Function must have at least one argument'
        return func_parameters, args_name

    def _get_annotated(self, func, args_name):
        annotated = _t.get_type_hints(func)
        if __debug__:
            annotated.pop(args_name, None)
            assert self._properties or annotated or self._default is not ignore, (
                'Some properties, annotations or a default property different '
                'to `ignore` must be specified')
        return annotated

    def _redirect(self, *args) -> _T_co:
        if len(self._properties) < len(args):
            it = _its.zip_longest(self._properties, args,
                                  fillvalue=self._default)
        else:
            it = zip(self._properties, args)
        vs, surplus = zip(*(g(a) for g, a in it))
        func = self._table.get(vs, _t.cast(
            _t.Callable[..., _T_co], self.__wrapped__))
        parameters, args_name = self._get_parameters(func)
        if not args_name:
            surplus = ()
        if func is not self.__wrapped__:
            return self._table[vs](*args, *surplus)
        else:
            try:
                return func(*args[:len(parameters)], *surplus)
            except TypeError as t:
                raise TypeError(
                    f'TypeError raised after trying to call default function: \n\t{t!s}')

    def _register_values(self, v, f):
        if __debug__ and v in self._table:
            _warn('Set of values already registered')
        self._table[v] = f

    def _process_hints(self, hints):
        product_values = []
        for h in hints:
            product_values.append(self._process_h(h))
        return product_values

    @staticmethod
    def _process_h(x):
        if isinstance(x, _t.GenericAlias):
            return (_t.get_origin(x),)
        elif _t.get_origin(x) is _t.Union:
            return [_t.get_origin(a) if isinstance(a, _t.GenericAlias) else a
                    for a in _t.get_args(x)]
        elif isinstance(x, ValuesUnion):
            return [a for a in x.args]
        else:
            return (x,)

    def register(
            self, func: _t.Optional[_t.Callable[..., _T_co]] = None, /, *,
            values: _t.Sequence[_t.Hashable] = (),
            default: _t.Hashable = _t.Any
    ) -> _t.Callable:
        def _register(f: _t.Callable[..., _T_co]) -> _t.Callable[..., _T_co]:
            nonlocal values
            assert isinstance(f, _t.Callable), \
                'Decorated object must be callable'
            assert isinstance(values, _t.Sequence), \
                '`properties` argument must be Sequence'
            assert isinstance(default, _t.Hashable), \
                'default must be hashable'
            f_parameters, args_name = self._get_parameters(f)
            annotated = self._get_annotated(f, args_name)
            assert len(values) <= len(f_parameters), \
                'values length must be less or equal the amount of arguments'
            it = _its.zip_longest(values, f_parameters, fillvalue=None)
            if len(self._properties) < len(f_parameters):
                it = _its.zip_longest(it, self._properties,
                                      fillvalue=self._default)
            else:
                it = zip(it, self._properties)

            values = []
            for (v, param), prop in it:
                if prop is ignore:
                    assert v in (None, _t.Any), (
                        f'{param.name} is supposed to be ignorated, '
                        'so typing.Any or no value should be provided')
                    values.append(_t.Any)
                elif not v:
                    try:
                        values.append(annotated[param.name])
                    except KeyError:
                        values.append(default)
                else:
                    values.append(v)
            for v in _its.product(*self._process_hints(values)):
                self._register_values(v, f)
            return f

        assert self.__wrapped__ is not None, (
            'object must be completed with a new call to decorate a function')

        if func is None:
            return _register
        else:
            return _register(func)

    def dispatch(self, *values: _t.Hashable) -> _t.Callable[..., _T_co]:
        assert self.__wrapped__ is not None, (
            'object must be completed with a new call to decorate a function')
        return self._table.get(values, self.__wrapped__)

    @property
    def registry(self) -> _MappingProxyType[tuple[object, ...], _t.Callable[..., _T_co]]:
        assert self.__wrapped__ is not None, (
            'object must be completed with a new call to decorate a function')
        return _MappingProxyType(self._table)


class TDecorableDescriptor(_t.Protocol[_T_co]):
    def __get__(self, obj, cls=None) -> _t.Callable[..., _T_co]: ...
    __call__: _t.Callable[..., _T_co]


class MultimethodByEquality(MultifunctionByEquality[_T_co]):
    """This class is the descriptor version of `MultifunctionByEquality`.

    A `first` option is provided for explícitly setting property and
    value, respectively, of the first parameter of the decorated function.
    In the constructor, if `first` is `None` and the first parameter is not
    annotated, its property will be `ignore`.
    In `register` the value will be `typing.Any` under the same conditions.

    >>> class A:
    ...     @MultimethodByEquality
    ...     def f(self, a, b):
    ...         return 'default method'
    ...
    ...     @f.register
    ...     def _(self, x: int, y: float):
    ...         return 'the other method'

    >>> assert A().f(3, 4) == 'default method'
    >>> assert A().f(3, 4.5) == 'the other method'
    >>> from typing import Any
    >>> from dataclasses import dataclass
    >>> @dataclass
    ... class B:
    ...     attribute: int
    ...
    ...     @MultimethodByEquality(first=lambda x: (x.attribute, x.attribute), default=ignore)
    ...     def method(self, other: int):
    ...         return self.attribute + other
    ...
    ...     @method.register
    ...     def _(self: 4, other: int):
    ...         return self.attribute * other
    ...
    ...     @method.register(first=5)
    ...     def _(self, other: int, *args):
    ...         assert args == (self.attribute, None)
    ...         return 'Allright'

    >>> assert B(3).method(4) == 7
    >>> assert B(4).method(3) == 12
    >>> assert B(5).method(3) == 'Allright'
    >>> assert B.method.dispatch('4', 5) is B.method.dispatch(3, 4)
    """

    def __init__(
            self, func: _t.Optional[TDecorableDescriptor] = None,
            properties: _t.Sequence[_t.Callable[[
                _t.Any], tuple[_t.Hashable, _t.Any]]] = (),
            default: _t.Callable[[_t.Any],
                                 tuple[_t.Hashable, _t.Any]] = get_type,
            first: _t.Callable[[_t.Any], tuple[_t.Hashable, _t.Any]] = _default_first):
        self._first = first
        super().__init__(func, properties, default)
        self.__isabstractmethod__ = \
            getattr(func, '__isabstractmethod__', False)

    def _complete(self, func: _t.Callable[..., _T_co]) -> 'MultimethodByEquality[_T_co]':
        assert hasattr(func, '__get__') and isinstance(
            func, _t.Callable), 'func must be a method'
        self._properties = self._get_with_first(
            func, self._properties, self._first, ignore)
        return _t.cast(MultimethodByEquality, super()._complete(func))

    def __get__(self, obj, cls=None):
        @_fts.wraps(self)
        def f(*args):
            return self(obj, *args)
        if obj is None:
            return self
        else:
            return f

    @staticmethod
    def _get_with_first(func, sequence, first, default_first):
        first_param = tuple(
            _insp.signature(func).parameters.values())[0]
        assert first_param.kind not in (_insp.Parameter.KEYWORD_ONLY,
                                        _insp.Parameter.VAR_KEYWORD,
                                        _insp.Parameter.VAR_POSITIONAL),  (
            'First parameter can not be keyword only, nor variable positional')
        if first is _default_first and \
                first_param.annotation is _insp.Parameter.empty:
            sequence = [default_first] + list(sequence)
        elif first is _default_first:
            sequence = [_t.get_type_hints(
                func)[first_param.name]] + list(sequence)
        else:
            sequence = [first] + list(sequence)
        return sequence

    def register(
        self, func: _t.Optional[_t.Callable[..., _T_co]] = None, /, *,
        values: _t.Sequence[_t.Hashable] = (),
        default: _t.Hashable = _t.Any,
        first: _t.Hashable = _default_first
    ) -> _t.Callable:
        def w(f):
            return MultifunctionByEquality.register(
                self, f,
                values=self._get_with_first(f, values, first, _t.Any),
                default=default)

        if func:
            return w(func)
        else:
            return w


__all__ = ['MultifunctionByEquality',
           'MultimethodByEquality',
           'ValuesUnion',
           'same', 'ignore', 'get_type']
