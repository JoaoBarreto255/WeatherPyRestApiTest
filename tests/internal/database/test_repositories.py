import asyncio

from fastapi import HTTPException
import pytest
from pytest_mock.plugin import MockerFixture

from internal.models import CityInfo, User, UserCityData
from internal.database.manager import AsyncDbManager
from internal.database.repositories import (
    BaseRepository,
    CityInfoRepository,
    UserRepository,
    UserCityDataRepository,
)
from tests.internal.database.test_manager import build_manager


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
    redis.hgetall.return_value = {b"index": b"1", b"created_at": b"2012-01-01"}

    asyncio.run(test_get_user(manager, 1))

    redis.hgetall.return_value = None
    with pytest.raises(HTTPException):
        asyncio.run(test_get_user(manager, 5))


def test_base_repository(mocker) -> None:
    manager, _, _ = build_manager(mocker, None)
    repo = BaseRepository(manager)

    assert repo.database_manager is not None
    assert repo.database_manager is manager


def test_user_city_data_repository_get_all_user_city_data(
    mocker: MockerFixture,
) -> None:
    manager = mocker.MagicMock()
    manager.find_all_by_field = mocker.AsyncMock()
    manager.find_all_by_field.return_value = []
    user_city_data_repo = UserCityDataRepository(manager)

    async def do_test():
        result = await user_city_data_repo.get_all_user_city_data(
            User(index=1, created_at="2021-02-02")
        )
        assert result == []
        manager.find_all_by_field.assert_called_once()
        manager.find_all_by_field.assert_awaited_with(
            UserCityData, "user_id", 1
        )

    asyncio.run(do_test())


def test_city_info_repository_new_cities(mocker: MockerFixture) -> None:
    counter = 0

    async def mocked_insert_registry(value):
        nonlocal counter
        counter += 1
        assert isinstance(value, CityInfo)
        assert value.api_id == counter

    manager = mocker.MagicMock()
    manager.insert_registry = mocked_insert_registry
    repo = CityInfoRepository(manager)

    async def do_assert():
        result = await repo.new_cities(1, 2, 3)

        assert len(result) == 3
        for i in range(3):
            assert isinstance(result[i], CityInfo)
            assert result[i].api_id == i + 1

        assert counter == 3

    asyncio.run(do_assert())


def test_city_info_repository_total_of_cities(mocker: MockerFixture) -> None:
    manager = mocker.MagicMock()
    manager.model_total_registries = mocker.AsyncMock()
    manager.model_total_registries.return_value = 10
    repo = CityInfoRepository(manager)

    async def do_assert():
        result = await repo.total_of_cities()
        assert result == 10
        manager.model_total_registries.assert_called_once()
        manager.model_total_registries.assert_awaited_with(CityInfo)

    asyncio.run(do_assert())
