from __future__ import annotations
from typing import Any, Callable, overload, Concatenate

class Pipable[T]:

    '''
    DOT PIPE STYLE
    --------------
    Pipable(1).func().value
        = func(1)
    Pipable(1).func(2).value
        = func(1, 2)
    Pipable(1).func(2, 3, 4).value
        = func(1, 2, 3, 4)
    Pipable(1).func(a = 5, b = 6).value
        = func(1, a = 5, b = 6)
    Pipable(1).func(2, a = 5, b = 6).value
        = func(1, 2, a = 5, b = 6)
    Pipable(1).func(2, 3, 4, a = 5, b = 6).value
        = func(1, 2, 3, 4, a = 5, b = 6)

    SHIFT PIPE STYLE
    ----------------
    Pipable(1) >> func >> Pipable.VALUE
        = func(1)
    Pipable(1) >> (func, 2) >> Pipable.VALUE
        = func(1, 2)
    Pipable(1) >> (func, (2, 3, 4)) >> Pipable.VALUE
        = func(1, 2, 3, 4)
    Pipable(1) >> (func, dict(a = 5, b = 6)) >> Pipable.VALUE
        = func(1, a = 5, b = 6)
    Pipable(1) >> (func, 2, dict(a = 5, b = 6)) >> Pipable.VALUE
        = func(1, 2, a = 5, b = 6)
    Pipable(1) >> (func, (2, 3, 4), dict(a = 5, b = 6)) >> Pipable.VALUE
        = func(1, 2, 3, 4, a = 5, b = 6)
    '''

    class ValueGetter:
        pass

    VALUE: ValueGetter = ValueGetter()
    BUILT_IN_CALLABLES: dict[str, Callable] = {
        name: getattr(__import__('builtins'), name)
        for name in dir(__import__('builtins'))
        if callable(getattr(__import__('builtins'), name))
    }
    ALL_AVAILABLE_CALLABLES: dict[str, Callable] = BUILT_IN_CALLABLES.copy()
    GET_AVAILABLE_CALLABLES: str = \
        "{key: value for key, value in (globals() | locals()).items() if callable(value)}"

    @classmethod
    def set_available_callables(cls, available_callables: dict[str, Callable]) -> None:
        cls.ALL_AVAILABLE_CALLABLES = cls.BUILT_IN_CALLABLES | available_callables

    def __init__(self, value: T, lookup_free_before_attr: bool = False) -> None:
        self.value: T = value
        self.lookup_free_before_attr: bool = lookup_free_before_attr
    
    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return repr(self.value)
    
    def set_lookup_free_before_attr(self, lookup_free_before_attr: bool) -> Pipable[T]:
        self.lookup_free_before_attr = lookup_free_before_attr
        return self
    
    def __call__(self, *args: Any, **kwargs: Any) -> Pipable:
        assert callable(self.value)
        return Pipable(self.value(*args, **kwargs), self.lookup_free_before_attr)
    
    def __getattr__(self, attr: str) -> Pipable:

        if not self.lookup_free_before_attr and hasattr(self.value, attr):
            return Pipable(getattr(self.value, attr), self.lookup_free_before_attr)
        
        if attr in Pipable.ALL_AVAILABLE_CALLABLES:
            return Pipable(lambda *args, **kwargs: Pipable.ALL_AVAILABLE_CALLABLES[attr](
                self.value, *args, **kwargs
            ), self.lookup_free_before_attr)
        
        if self.lookup_free_before_attr and hasattr(self.value, attr):
            return Pipable(getattr(self.value, attr), self.lookup_free_before_attr)

        raise AttributeError

    # func() has >= 3 arguments & func() has **kwargs
    @overload
    def __rshift__[**P, R](
        self, func_and_args: tuple[Callable[Concatenate[T, P], R], tuple[Any, ...], dict[str, Any]]
    ) -> Pipable[R]: ...

    # func() has 2 arguments & func() has **kwargs
    @overload
    def __rshift__[S, R](
        self, func_and_args: tuple[Callable[[T, S], R], S, dict[str, Any]]
    ) -> Pipable[R]: ...

    # func() has 1 argument & func() has **kwargs
    @overload
    def __rshift__[R](
        self, func_and_args: tuple[Callable[[T], R], dict[str, Any]]
    ) -> Pipable[R]: ...

    # func() has >= 3 arguments
    @overload
    def __rshift__[**P, R](
        self, func_and_args: tuple[Callable[Concatenate[T, P], R], tuple[Any, ...]]
    ) -> Pipable[R]: ...

    # func() has 2 arguments
    @overload
    def __rshift__[S, R](self, func_and_args: tuple[Callable[[T, S], R], S]) -> Pipable[R]: ...

    # func() has 1 argument
    @overload
    def __rshift__[R](self, func_and_args: Callable[[T], R]) -> Pipable[R]: ...

    # piping just to get the final value
    @overload
    def __rshift__(self, func_and_args: Pipable.ValueGetter) -> T: ...

    def __rshift__(
        self, func_and_args:
            tuple[Callable, tuple[Any, ...], dict[str, Any]] |
            tuple[Callable, Any, dict[str, Any]] |
            tuple[Callable, dict[str, Any]] |
            tuple[Callable, tuple[Any, ...]] |
            tuple[Callable, Any] |
            Callable |
            Pipable.ValueGetter
    ) -> Pipable | T:
        
        f: Any = func_and_args
        arg_to_result_map: dict[Callable[[], bool], Callable[[], Any]] = {
            lambda: callable(f):
                lambda: Pipable(f(self.value)),
            lambda: isinstance(f, Pipable.ValueGetter):
                lambda: self.value,
            lambda: isinstance(f, tuple) and len(f) == 2 and isinstance(f[1], tuple):
                lambda: Pipable(f[0](self.value, *f[1])),
            lambda: isinstance(f, tuple) and len(f) == 2 and isinstance(f[1], dict):
                lambda: Pipable(f[0](self.value, **f[1])),
            lambda: isinstance(f, tuple) and len(f) == 2:
                lambda: Pipable(f[0](self.value, f[1])),
            lambda: isinstance(f, tuple) and len(f) == 3 and isinstance(f[1], tuple):
                lambda: Pipable(f[0](self.value, *f[1], **f[2])),
            lambda: isinstance(f, tuple) and len(f) == 3:
                lambda: Pipable(f[0](self.value, f[1], **f[2]))
        }

        for predicate, result in arg_to_result_map.items():
            if predicate():
                return result()
            
        raise RuntimeError("code should never reach here")