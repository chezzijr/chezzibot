from inspect import FullArgSpec, getfullargspec
from typing import (
    Awaitable,
    Callable,
    Dict,
    ParamSpec,
    Sequence,
    TypeVar,
)

__all__ = [
    "allow_argument_cast",
    "allow_argument_cast_async"
]

T = TypeVar("T")
R = TypeVar("R")
P = ParamSpec("P")


def convert_kwargs(argspec: FullArgSpec, **kwargs: Dict[str, T]) -> Dict[str, T]:
    new_kwargs = {}
    for key, val in kwargs.items():
        arg_type = argspec.annotations.get(key)

        if arg_type is None or isinstance(arg_type, str):
            new_kwargs[key] = val
        else:
            new_kwargs[key] = arg_type(val)

    return new_kwargs


def convert_args(argspec: FullArgSpec, *args: Sequence[T]) -> Sequence[T]:
    new_args = []
    for i, arg in enumerate(args):
        arg_name = argspec.args[i]
        arg_type = argspec.annotations.get(arg_name)

        if arg_type is None or isinstance(arg_type, str):
            new_args.append(arg)
        else:
            new_args.append(arg_type(arg))

    return new_args


def allow_argument_cast(fn: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        argspec = getfullargspec(fn)
        new_args = convert_args(argspec, *args)
        new_kwargs = convert_kwargs(argspec, **kwargs)
        return fn(*new_args, **new_kwargs)

    return wrapper


def allow_argument_cast_async(fn: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        argspec = getfullargspec(fn)
        new_args = convert_args(argspec, *args)
        new_kwargs = convert_kwargs(argspec, **kwargs)
        return await fn(*new_args, **new_kwargs)

    return wrapper


@allow_argument_cast
def add(a: str, b: str) -> str:
    return a + b
