import asyncio

from fastapi import HTTPException
import pytest
from pytest_mock.plugin import MockerFixture

from internal.models import User
from internal.database.manager import AsyncDbManager
from internal.database.repositories import BaseRepository, UserRepository
from tests.internal.database.manager import build_manager

def test_user_repository_new_user(mocker: MockerFixture) -> None:
    async def test_new_user(manager, expected: int) -> None:
        repo = UserRepository(manager)
        result = await repo.new_user()
        assert result is not None
        assert isinstance(result, User)
        assert len(result.created_at) > 0
        assert expected == result.index

    manager, _, _ = build_manager(mocker, None)
    asyncio.run(test_new_user(manager, 1))

    manager, _, _ = build_manager(mocker, 4)
    asyncio.run(test_new_user(manager, 5))


def test_user_repository_get_user(mocker: MockerFixture) -> None:
    async def test_get_user(manager, index: int) -> None:
        repo = UserRepository(manager)
        result = await repo.get_user(index)
        assert result is not None
        assert isinstance(result, User)

    manager, redis, _ = build_manager(mocker, None)
    redis.hgetall = mocker.AsyncMock()
    redis.hgetall.return_value = {b'index': b'1', b'created_at': b'2012-01-01'}
 
    asyncio.run(test_get_user(manager, 1))

    redis.hgetall.return_value = None
    with pytest.raises(HTTPException):
        asyncio.run(test_get_user(manager, 5))

def test_base_repository(mocker) -> None:
    manager, _, _ = build_manager(mocker, None)
    repo = BaseRepository(manager)

    assert repo.database_manager is not None
    assert repo.database_manager is manager
