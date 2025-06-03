from __future__ import annotations

import copy
from functools import wraps
from typing import Callable, Generic, TypeVar, Union

from .exception import UnwrapError

T = TypeVar("T")
E = TypeVar("E")
_T = TypeVar("_T")
_E = TypeVar("_E")
U = TypeVar("U")
F = TypeVar("F")
V = TypeVar("V")


class Result(Generic[T, E]):
    class _Ok(Generic[_T]):
        def __init__(self, value: _T):
            self.value = value

    class _Err(Generic[_E]):
        def __init__(self, error: _E):
            self.error = error

    def __init__(self, v: Union[_Ok[T], _Err[E]]) -> None:
        self.res = v

    @classmethod
    def create_ok(cls, value: T) -> Result[T, E]:
        return Result(Result._Ok(value))

    @classmethod
    def create_err(cls, error: E) -> Result[T, E]:
        return Result(Result._Err(error))

    def is_ok(self):
        return isinstance(self.res, Result._Ok)

    def is_ok_and(self, f: Callable[[T], bool]):
        return isinstance(self.res, Result._Ok) and f(self.res.value)

    def is_err(self):
        return isinstance(self.res, Result._Err)

    def is_err_and(self, f: Callable[[E], bool]):
        return isinstance(self.res, Result._Err) and f(self.res.error)

    def ok(self) -> Option[T]:
        if isinstance(self.res, Result._Ok):
            return Option.create_some(self.res.value)
        else:
            return Option(None)

    def err(self) -> Option[E]:
        if isinstance(self.res, Result._Ok):
            return Option(None)
        else:
            return Option.create_some(self.res.error)

    def map(self, f: Callable[[T], U]) -> Result[U, E]:
        if isinstance(self.res, Result._Ok):
            return Result.create_ok(f(self.res.value))
        else:
            return self  # type: ignore

    def map_or(self, default: U, f: Callable[[T], U]) -> U:
        if isinstance(self.res, Result._Ok):
            return f(self.res.value)
        else:
            return default

    def map_or_else(self, default: Callable[[E], U], f: Callable[[T], U]) -> U:
        if isinstance(self.res, Result._Ok):
            return f(self.res.value)
        else:
            return default(self.res.error)

    def map_err(self, f: Callable[[E], F]) -> Result[T, F]:
        if isinstance(self.res, Result._Ok):
            return self  # type: ignore
        else:
            return Result.create_err(f(self.res.error))

    def inspect(self, f: Callable[[T], None]) -> Result[T, E]:
        if isinstance(self.res, Result._Ok):
            f(self.res.value)
        return self

    def inspect_err(self, f: Callable[[E], None]) -> Result[T, E]:
        if isinstance(self.res, Result._Err):
            f(self.res.error)
        return self

    def expect(self, msg: str) -> T:
        if isinstance(self.res, Result._Ok):
            return self.res.value
        else:
            raise UnwrapError(f"{msg}: {self.res.error}")

    def unwrap(self) -> T:
        if isinstance(self.res, Result._Ok):
            return self.res.value
        else:
            raise UnwrapError(f"called `Result.unwrap()` on a `Err` value: {self.res.error}")

    def unwrap_or(self, default: T) -> T:
        if isinstance(self.res, Result._Ok):
            return self.res.value
        else:
            return default

    def unwrap_or_default(self, default: Callable[[], T]) -> T:
        if isinstance(self.res, Result._Ok):
            return self.res.value
        else:
            return default()

    def unwrap_or_else(self, op: Callable[[E], T]) -> T:
        if isinstance(self.res, Result._Ok):
            return self.res.value
        else:
            return op(self.res.error)

    def into_ok(self) -> T:
        raise NotImplementedError

    def expect_err(self, msg: str) -> E:
        if isinstance(self.res, Result._Ok):
            raise UnwrapError(f"{msg}: {self.res.value}")
        else:
            return self.res.error

    def unwrap_err(self) -> E:
        if isinstance(self.res, Result._Ok):
            raise UnwrapError(f"called `Result.unwrap_err()` on a `Ok` value: {self.res.value}")
        else:
            return self.res.error

    def into_err(self) -> E:
        raise NotImplementedError

    def and_(self, res: Result[U, E]) -> Result[U, E]:
        if isinstance(self.res, Result._Ok):
            return res
        else:
            return self.res.error  # type: ignore

    def and_then(self, op: Callable[[T], Result[U, E]]) -> Result[U, E]:
        if isinstance(self.res, Result._Ok):
            return op(self.res.value)
        else:
            return self  # type: ignore

    def or_(self, res: Result[T, F]) -> Result[T, F]:
        if isinstance(self.res, Result._Ok):
            return self.res.value  # type: ignore
        else:
            return res

    def or_else(self, f: Callable[[E], Result[T, F]]) -> Result[T, F]:
        if isinstance(self.res, Result._Ok):
            return self  # type: ignore
        else:
            return f(self.res.error)

    def copy(self) -> Result[T, E]:
        if isinstance(self.res, Result._Ok):
            return Result.create_ok(copy.copy(self.res.value))
        else:
            return Result.create_err(copy.copy(self.res.error))

    def clone(self) -> Result[T, E]:
        if isinstance(self.res, Result._Ok):
            return Result.create_ok(copy.deepcopy(self.res.value))
        else:
            return Result.create_err(copy.deepcopy(self.res.error))

    def transpose(self) -> Option[Result[T, E]]:
        if isinstance(self.res, Result._Ok):
            assert isinstance(self.res.value, Option)
            if isinstance(self.res.value.optb, Option._Some):
                return Option.create_some(Result.create_ok(self.res.value.optb.value))
            else:
                return Option(None)
        else:
            return Option.create_some(Result.create_err(self.res.error))

    def flatten(self) -> Result[T, E]:
        if isinstance(self.res, Result._Ok):
            assert isinstance(self.res.value, Result)
            return self.res.value
        else:
            return self

    def __str__(self) -> str:
        if isinstance(self.res, Result._Ok):
            s = f"Ok({self.res.value})"
        else:
            s = f"Err({self.res.error})"
        return s

    def __repr__(self) -> str:
        s = f"<Result {hex(id(self))}\n"
        if isinstance(self.res, Result._Ok):
            s += f"    Ok {hex(id(self.res))}\n"
            s += f"        {repr(self.res.value)}\n"
        else:
            s += f"    Err {hex(id(self.res))}\n"
            s += f"        {repr(self.res.error)}\n"
        s += ">"
        return s

    def __hash__(self) -> int:
        if isinstance(self.res, Result._Ok):
            assert hasattr(self.res.value, "__hash__"), f"{type(self.res.value)} has no `__hash__` method"
            return hash(self.res.value)
        else:
            assert hasattr(self.res.error, "__hash__"), f"{type(self.res.error)} has no `__hash__` method"
            return hash(self.res.error)

    def __iter__(self):
        if isinstance(self.res, Result._Ok):
            yield self.res.value
        else:
            raise StopIteration

    @property
    def value(self):
        return self.unwrap()

    @property
    def error(self):
        return self.unwrap_err()


from .option import Option  # noqa: E402

Ok = Result[T, E].create_ok
Err = Result[T, E].create_err


def resultify(func: Callable[..., T]) -> Callable[..., Result[T, Exception]]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Result[T, Exception]:
        try:
            # Execute the function and wrap the result in Ok
            return Ok(func(*args, **kwargs))
        except Exception as e:
            # Catch exceptions and wrap them in Err
            return Err(e)

    return wrapper
