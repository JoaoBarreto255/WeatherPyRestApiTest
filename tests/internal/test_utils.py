import asyncio
import math
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


@pytest.mark.long
def test_make_async_decorator() -> None:
    @utils.make_async_decorator
    def test_async_fn(arg, sleep=1.0) -> None:
        start = time.time()
        time.sleep(sleep)
        delta = time.time() - start
        assert math.isclose(sleep, delta, rel_tol=1e-2)
        return arg

    assert 1 == asyncio.run(test_async_fn(1, 0.5))

    assert 2 == asyncio.run(test_async_fn(2, 2))


SUMMATION_OF_1_TO_100 = sum(range(1, 101))


def test_chunked_stream_chunck_size() -> None:
    """Check chunk size"""

    def test_chunk_stream(chunk_size: int) -> None:
        for chunk in utils.chunk_stream(range(1, 101), chunk_size):
            assert len(chunk) <= chunk_size

    for chunk_size in range(15, 1, -1):
        test_chunk_stream(chunk_size)


def test_chunked_stream_chunck_itens_integrety() -> None:
    """Check if every chunk are with correct elements"""

    def test_chunk_stream(chunk_size: int) -> None:
        chunk_data = [
            (sum(chunk), len(chunk))
            for chunk in utils.chunk_stream(range(1, 101), chunk_size)
        ]
        assert sum([s for s, _ in chunk_data]) == SUMMATION_OF_1_TO_100
        assert sum([c for _, c in chunk_data]) == 100

    for chk_sz in range(15, 1, -1):
        test_chunk_stream(chk_sz)
