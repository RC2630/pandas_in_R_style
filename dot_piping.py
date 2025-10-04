from __future__ import annotations
from typing import Any, Callable

class Pipable:

    '''
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
    '''

    ALL_AVAILABLE_CALLABLES: dict[str, Callable] = {}
    GET_AVAILABLE_CALLABLES: str = "{key: value for key, value in ({name: getattr(__import__('builtins'), name) for name in dir(__import__('builtins'))} | globals() | locals()).items() if callable(value)}"

    @classmethod
    def set_available_callables(cls, available_callables: dict[str, Callable]) -> None:
        cls.ALL_AVAILABLE_CALLABLES = available_callables

    def __init__(self, value: Any, lookup_free_before_attr: bool = False) -> None:
        self.value: Any = value
        self.lookup_free_before_attr: bool = lookup_free_before_attr
    
    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return repr(self.value)
    
    def set_lookup_free_before_attr(self, lookup_free_before_attr: bool) -> Pipable:
        self.lookup_free_before_attr = lookup_free_before_attr
        return self
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return Pipable(self.value(*args, **kwargs), self.lookup_free_before_attr)
    
    def __getattr__(self, attr: str) -> Any:

        if not self.lookup_free_before_attr and hasattr(self.value, attr):
            return Pipable(getattr(self.value, attr), self.lookup_free_before_attr)
        
        if attr in Pipable.ALL_AVAILABLE_CALLABLES:
            return Pipable(lambda *args, **kwargs: Pipable.ALL_AVAILABLE_CALLABLES[attr](
                self.value, *args, **kwargs
            ), self.lookup_free_before_attr)
        
        if self.lookup_free_before_attr and hasattr(self.value, attr):
            return Pipable(getattr(self.value, attr), self.lookup_free_before_attr)

        raise AttributeError