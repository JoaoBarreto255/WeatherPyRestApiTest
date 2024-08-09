import asyncio

from fastapi import HTTPException
import pytest
from pytest_mock.plugin import MockerFixture

from internal.database.manager import AsyncDbManager, TABLE_DATA_ITEM_TOTAL_KEY
from internal.models import User

EXPECTED_KEY = f"table_data:{User.table_name()}"


def build_pipe_mock(mocker: MockerFixture, hget_return=None):
    pipe = mocker.MagicMock()
    pipe.watch = mocker.AsyncMock(spec=None)
    pipe.watch.return_value = None
    pipe.unwatch = mocker.AsyncMock(spec=None)
    pipe.unwatch.return_value = None
    pipe.hset = mocker.AsyncMock()
    pipe.hset.return_value = None
    pipe.hget = mocker.AsyncMock()

    if not callable(hget_return):
        pipe.hget.return_value = hget_return
    else:
        pipe.hget.side_effect = hget_return

    pipe.hincrby = mocker.AsyncMock()
    pipe.hincrby.return_value = None
    pipe.__aenter__ = mocker.AsyncMock()
    pipe.__aenter__.return_value = pipe
    pipe.__aexit__ = mocker.AsyncMock()
    pipe.__aexit__.return_value = False
    return pipe


def build_manager(mocker, curr):
    pipe = build_pipe_mock(mocker, curr)
    redis = mocker.MagicMock()
    redis.pipeline.return_value = pipe

    manager = AsyncDbManager(redis)
    manager.redis = redis  # fix singleton issue

    return manager, redis, pipe


def test_pipeline_create_resgistry_index(
    mocker: MockerFixture,
):
    """Test for generate new index for entity registry"""

    async def test(expected, curr):
        manager, redis, pipe = build_manager(mocker, curr)
        result = await manager._pipeline_create_resgistry_index(
            User(created_at="2024-02-01")
        )

        redis.pipeline.assert_called_once()

        pipe.watch.assert_awaited_with(EXPECTED_KEY)
        pipe.unwatch.assert_called_once()
        pipe.hget.assert_awaited_with(EXPECTED_KEY, TABLE_DATA_ITEM_TOTAL_KEY)

        if curr is not None:
            pipe.hincrby.assert_awaited_with(
                EXPECTED_KEY, TABLE_DATA_ITEM_TOTAL_KEY
            )
            pipe.hset.assert_not_called()
            assert expected == result

            return

        pipe.hset.assert_awaited_with(
            EXPECTED_KEY, TABLE_DATA_ITEM_TOTAL_KEY, 1
        )
        pipe.hincrby.assert_not_called()
        assert expected == result

    asyncio.run(test(1, None))
    asyncio.run(test(2, b"1"))
    asyncio.run(test(3, b"2"))
    asyncio.run(test(4, b"3"))
    asyncio.run(test(5, b"4"))


def test__pipeline_set_resgistry_fields(mocker: MockerFixture):
    async def test_case(user: User, **kwargs):
        manager, redis, pipe = build_manager(mocker, None)
        await manager._pipeline_set_resgistry_fields(user)
        pipe.watch.assert_called_once()
        pipe.watch.assert_awaited_with(user_index := user.db_index())
        pipe.unwatch.assert_called_once()
        pipe.hincrby.assert_not_called()
        pipe.hget.assert_not_called()
        for key, value in kwargs.items():
            pipe.hset.assert_any_call(user_index, key, value)

    asyncio.run(
        test_case(
            User(index=1, created_at="2024-02-02"),
            index=1,
            created_at="2024-02-02",
        )
    )
    asyncio.run(
        test_case(
            User(index=1, created_at="2024-02-02", requested_at="2024-02-03"),
            index=1,
            created_at="2024-02-02",
            requested_at="2024-02-03",
        )
    )
    asyncio.run(
        test_case(
            User(
                index=1,
                created_at="2024-02-02",
                requested_at="2024-02-03",
                processed_at="2024-08-09",
            ),
            index=1,
            created_at="2024-02-02",
            requested_at="2024-02-03",
            processed_at="2024-08-09",
        )
    )


def test_find_registry(mocker: MockerFixture) -> None:
    redis = mocker.MagicMock()
    redis.hgetall = mocker.AsyncMock()
    manager = AsyncDbManager(redis)
    manager.redis = redis

    redis.hgetall.return_value = {b"index": b"1", b"created_at": b"2024-02-02"}

    async def success():
        result = await manager.find_registry(User, 1)
        redis.hgetall.assert_called_once()
        redis.hgetall.assert_awaited_with(f"{User.table_name()}_1")
        assert isinstance(result, User)
        assert 1 == result.index
        assert "2024-02-02" == result.created_at
        assert result.processed_at is None
        assert result.requested_at is None

    asyncio.run(success())

    async def fail():
        await manager.find_registry(User, 1)

    redis.hgetall.return_value = None
    with pytest.raises(HTTPException):
        asyncio.run(fail())

    redis.hgetall.return_value = {}
    with pytest.raises(HTTPException):
        asyncio.run(fail())


def test_update_registry(mocker) -> None:
    async def run_test(user: User):
        manager, _, _ = build_manager(mocker, None)
        await manager.update_registry(user)
        assert True

    asyncio.run(run_test(User(index=1, created_at="2024-02-02")))

    with pytest.raises(HTTPException):
        asyncio.run(run_test(User(created_at="2024-02-02")))


def test_insert_registry(mocker) -> None:
    async def run_test(
        user: User, expected: int, current_index: int | None = None
    ):
        manager, _, _ = build_manager(mocker, current_index)
        await manager.insert_registry(user)
        assert expected == user.index

    asyncio.run(run_test(User(created_at="2012-09-08"), 1))
    asyncio.run(run_test(User(created_at="2012-09-08"), 2, 1))
    asyncio.run(run_test(User(created_at="2012-09-08"), 5, 4))
