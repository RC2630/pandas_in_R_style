from __future__ import annotations
from typing import Any, Callable, overload

class Pipable:

    '''
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

    def __init__(self, value: Any) -> None:
        self.value: Any = value
    
    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return repr(self.value)

    # func() has >= 3 arguments & func() has **kwargs
    @overload
    def __rshift__(
        self, func_and_args: tuple[Callable, tuple[Any, ...], dict[str, Any]]
    ) -> Pipable: ...

    # func() has 2 arguments & func() has **kwargs
    @overload
    def __rshift__(self, func_and_args: tuple[Callable, Any, dict[str, Any]]) -> Pipable: ...

    # func() has 1 argument & func() has **kwargs
    @overload
    def __rshift__(self, func_and_args: tuple[Callable, dict[str, Any]]) -> Pipable: ...

    # func() has >= 3 arguments
    @overload
    def __rshift__(self, func_and_args: tuple[Callable, tuple[Any, ...]]) -> Pipable: ...

    # func() has 2 arguments
    @overload
    def __rshift__(self, func_and_args: tuple[Callable, Any]) -> Pipable: ...

    # func() has 1 argument
    @overload
    def __rshift__(self, func_and_args: Callable) -> Pipable: ...

    # piping just to get the final value
    @overload
    def __rshift__(self, func_and_args: Pipable.ValueGetter) -> Any: ...

    def __rshift__(
        self, func_and_args:
            tuple[Callable, tuple[Any, ...], dict[str, Any]] |
            tuple[Callable, Any, dict[str, Any]] |
            tuple[Callable, dict[str, Any]] |
            tuple[Callable, tuple[Any, ...]] |
            tuple[Callable, Any] |
            Callable |
            Pipable.ValueGetter
    ) -> Pipable | Any:
        
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