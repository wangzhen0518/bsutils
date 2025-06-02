from __future__ import annotations

import copy
from functools import wraps
from typing import Callable, Generic, TypeVar, Union

from .exception import UnwrapError

T = TypeVar("T")
E = TypeVar("E")
_T = TypeVar("_T")
U = TypeVar("U")
V = TypeVar("V")


class Option(Generic[T]):
    class _Some(Generic[_T]):
        def __init__(self, value: _T) -> None:
            super().__init__()
            self.value = value

    def __init__(self, value: Union[_Some, None]) -> None:
        super().__init__()
        self.optb = value

    @classmethod
    def create_some(cls, value: T) -> Option[T]:
        return Option(Option._Some(value))

    @classmethod
    def create_none(cls) -> Option[T]:
        return Option(None)

    def is_some(self) -> bool:
        return isinstance(self.optb, Option._Some)

    def is_some_and(self, f: Callable[[T], bool]) -> bool:
        return isinstance(self.optb, Option._Some) and f(self.optb.value)

    def is_none(self) -> bool:
        return self.optb is None

    def is_none_or(self, f: Callable[[T], bool]) -> bool:
        return self.optb is None or f(self.optb.value)

    def expect(self, msg: str) -> T:
        if isinstance(self.optb, Option._Some):
            return self.optb.value
        else:
            raise UnwrapError(msg)

    def unwrap(self) -> T:
        if isinstance(self.optb, Option._Some):
            return self.optb.value
        else:
            raise UnwrapError("called `Option.unwrap()` on a `None` value")

    def unwrap_or(self, default: T) -> T:
        if isinstance(self.optb, Option._Some):
            return self.optb.value
        else:
            return default

    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        if isinstance(self.optb, Option._Some):
            return self.optb.value
        else:
            return f()

    unwrap_or_default = unwrap_or_else

    def map(self, f: Callable[[T], U]) -> Option[U]:
        if isinstance(self.optb, Option._Some):
            return Option.create_some(f(self.optb.value))
        else:
            return Option(None)

    def map_or(self, default: U, f: Callable[[T], U]) -> U:
        if isinstance(self.optb, Option._Some):
            return f(self.optb.value)
        else:
            return default

    def map_or_else(self, default: Callable[[], U], f: Callable[[T], U]) -> U:
        if isinstance(self.optb, Option._Some):
            return f(self.optb.value)
        else:
            return default()

    def inspect(self, f: Callable[[T], None]) -> Option[T]:
        if isinstance(self.optb, Option._Some):
            f(self.optb.value)
        return self

    def ok_or(self, error: E) -> Result[T, E]:
        if isinstance(self.optb, Option._Some):
            return Result.create_ok(self.optb.value)
        else:
            return Result.create_err(error)

    def ok_or_else(self, f: Callable[[], E]) -> Result[T, E]:
        if isinstance(self.optb, Option._Some):
            return Result.create_ok(self.optb.value)
        else:
            return Result.create_err(f())

    def and_(self, optb: Option[U]) -> Option[U]:
        if isinstance(self.optb, Option._Some):
            return optb
        else:
            return Option(None)

    def and_then(self, f: Callable[[T], Option[U]]) -> Option[U]:
        if isinstance(self.optb, Option._Some):
            return f(self.optb.value)
        else:
            return Option(None)

    def filter(self, f: Callable[[T], bool]) -> Option[T]:
        if isinstance(self.optb, Option._Some) and f(self.optb.value):
            return self
        else:
            return Option(None)

    def or_(self, optb: Option[T]) -> Option[T]:
        if isinstance(self.optb, Option._Some):
            return self
        else:
            return optb

    def or_else(self, f: Callable[[], Option[T]]) -> Option[T]:
        if isinstance(self.optb, Option._Some):
            return self
        else:
            return f()

    def xor(self, optp: Option[T]) -> Option[T]:
        if isinstance(self.optb, Option._Some) and isinstance(optp.optb, Option._Some):
            return Option(None)
        elif isinstance(self.optb, Option._Some):
            return self
        else:
            return optp

    def insert(self, value: T) -> Option[T]:
        self.optb = Option._Some(value)
        return self

    def get_or_insert(self, value: T) -> T:
        if self.optb is None:
            self.optb = Option._Some(value)
        return self.optb.value

    def get_or_insert_with(self, f: Callable[[], T]) -> T:
        if self.optb is None:
            self.optb = Option._Some(f())
        return self.optb.value

    get_or_insert_default = get_or_insert_with

    def take(self) -> Option[T]:
        if isinstance(self.optb, Option._Some):
            value = self.optb.value
            self.optb = None
            return Option.create_some(value)
        else:
            return Option(None)

    def take_if(self, f: Callable[[T], bool]) -> Option[T]:
        if isinstance(self.optb, Option._Some) and f(self.optb.value):
            value = self.optb.value
            self.optb = None
            return Option.create_some(value)
        else:
            return Option(None)

    def replace(self, value: T) -> Option[T]:
        if isinstance(self.optb, Option._Some):
            old_value = self.optb.value
            self.optb = Option._Some(value)
            return Option.create_some(old_value)
        else:
            self.optb = Option._Some(value)
            return Option(None)

    def zip(self, other: Option[U]) -> "Option[tuple[T, U]]":
        if isinstance(self.optb, Option._Some) and isinstance(other.optb, Option._Some):
            return Option.create_some((self.optb.value, other.optb.value))
        else:
            return Option(None)

    def zip_with(self, other: Option[U], f: Callable[[T, U], V]) -> "Option[V]":
        if isinstance(self.optb, Option._Some) and isinstance(other.optb, Option._Some):
            return Option.create_some(f(self.optb.value, other.optb.value))
        else:
            return Option(None)

    def unzip(self) -> tuple[Option[T], Option[U]]:  # type: ignore
        if isinstance(self.optb, Option._Some):
            assert isinstance(self.optb.value, tuple) and len(self.optb.value) == 2, "Option.unzip() requires a tuple of length 2"
            return Option.create_some(self.optb.value[0]), Option.create_some(self.optb.value[1])
        else:
            return Option(None), Option(None)

    def copy(self) -> Option[T]:
        if isinstance(self.optb, Option._Some):
            return Option.create_some(copy.copy(self.optb.value))
        else:
            return Option(None)

    def clone(self) -> Option[T]:
        if isinstance(self.optb, Option._Some):
            return Option.create_some(copy.deepcopy(self.optb.value))
        else:
            return Option(None)

    def transpose(self) -> Result[Option[T], E]:  # type: ignore
        if isinstance(self.optb, Option._Some):
            return Result.create_ok(Option.create_some(self.optb.value))
        else:
            return Result.create_err(None)

    def flatten(self) -> Option[T]:
        if isinstance(self.optb, Option._Some):
            assert isinstance(self.optb.value, Option)
            return self.optb.value
        else:
            return Option(None)

    def __iter__(self):
        if isinstance(self.optb, Option._Some):
            yield self.optb.value
        else:
            raise StopIteration

    def __str__(self) -> str:
        if isinstance(self.optb, Option._Some):
            return f"Some({self.optb.value})"
        else:
            return "None"

    def __repr__(self) -> str:
        if isinstance(self.optb, Option._Some):
            return f"<Option {id(self)}\n  >" + f"    Some {id(self.optb)}\n" + f"        {repr(self.optb.value)}\n>"
        else:
            return f"<Option {id(self)}\n    None\n>"

    def __hash__(self) -> int:
        if isinstance(self.optb, Option._Some):
            assert hasattr(self.optb.value, "__hash__"), f"{type(self.optb.value)} has no `__hash__` method"
            return hash(self.optb.value)
        else:
            return 0


from .result import Result  # noqa: E402

Some = Option[T].create_some
Null = Option[T].create_none


def optionalify(func: Callable[..., T], catch_exceptions: bool = True) -> Callable[..., Option[T]]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Option[T]:
        if catch_exceptions:
            try:
                result = func(*args, **kwargs)
            except Exception:
                return Null()
        else:
            result = func(*args, **kwargs)

        if result is None:
            return Null()
        else:
            return Some(result)

    return wrapper
