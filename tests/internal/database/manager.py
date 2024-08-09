import asyncio

import pytest
import pytest_mock
from pytest_mock.plugin import MockerFixture
from redis.asyncio import Redis

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


def test_pipeline_create_resgistry_index(
    mocker: MockerFixture,
):
    """Test for generate new index for entity registry"""

    async def test(expected, curr):
        pipe = build_pipe_mock(mocker, curr)
        redis = mocker.MagicMock()
        redis.pipeline.return_value = pipe

        manager = AsyncDbManager(redis)
        manager.redis = redis  # fix singleton issue
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
