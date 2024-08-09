import asyncio
import time

import pytest

import internal.utils as utils



def test_build_singleton() -> None:
    @utils.build_singleton
    class TestSingle:
        def __init__(self, val) -> None:
            self.value = val

    object_a = TestSingle(1)
    object_b = TestSingle(2)

    assert object_a is object_b
    assert object_a.value == object_b.value
    assert object_b.value == 1

    object_b.value = 3
    assert object_a.value == 3

def test_make_async_decorator() -> None:
    @utils.make_async_decorator
    def test_async_fn(arg, sleep=1.0) -> None:
        start = time.time()
        time.sleep(sleep)
        delta = time.time() - start
        assert sleep <= delta <= sleep + 0.2
        return arg

    assert 1 == asyncio.run(test_async_fn(1, 0.5))

    assert 2 == asyncio.run(test_async_fn(2, 2))
    