import asyncio
import functools

from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar, Callable, Iterable, Generator


CLS = TypeVar("CLS")
__EXECUTOR = ThreadPoolExecutor(4)


def build_singleton(cls: CLS):
    """Wrapper for build singleton class"""

    @functools.wraps(cls)
    def wrapper(*args, **kwargs) -> CLS:
        if wrapper.instance is None:
            wrapper.instance = cls(*args, **kwargs)

        return wrapper.instance

    wrapper.instance = None

    return wrapper


def make_async_decorator(func: Callable):
    """Transform methods in async methods"""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        executor = asyncio.get_running_loop()
        return await executor.run_in_executor(
            __EXECUTOR, lambda: func(*args, **kwargs)
        )

    return wrapper


def chunk_stream(iterable: Iterable, chunk_size: int) -> Generator:
    """Split stream data in small array chunks"""

    chunck = []
    for item in iterable:
        if len(chunck) == chunk_size:
            yield chunck
            chunck = []
        chunck.append(item)

    if len(chunck) > 0:
        yield chunck
