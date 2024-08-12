"""Module for querie and save data"""

import json
from datetime import datetime
from typing import Annotated

import click
from fastapi import Depends

from internal.settings import _api_settings_builder
from internal.database.manager import (
    AsyncDbManagerDI,
    AsyncDbManager,
    _redis_di_factory,
)
from internal.models import User, UserCityData, CityInfo, Base


class BaseRepository:
    """common repository logic"""

    def __init__(self, manager: AsyncDbManagerDI) -> None:
        self.database_manager = manager

    async def insert(self, registry: Base) -> None:
        """Save registry in database"""

        await self.database_manager.insert_registry(registry)

    async def update(self, registry: Base) -> None:
        """Update user city data request in database"""

        await self.database_manager.update_registry(registry)


class UserRepository(BaseRepository):
    """
    Api User repository
    """

    async def new_user(self) -> User:
        """Create new user for download weather state"""
        user = User(created_at=datetime.now().isoformat())
        await self.insert(user)

        return user

    async def get_user(self, index: int) -> User:
        """Fecth user data"""
        return await self.database_manager.find_registry(User, index)

    async def remove_all_users(self) -> None:
        """Clear all users saved in database"""
        await self.database_manager.clear_model_registries(User)


class UserCityDataRepository(BaseRepository):
    """Repository for user request data"""

    async def get_all_user_city_data(self, user: User) -> list[UserCityData]:
        """Get all user city data point from one user"""

        return await self.database_manager.find_all_by_field(
            UserCityData, "user_id", user.index
        )


class CityInfoRepository(BaseRepository):
    """Repository to store Cities ids to request"""

    async def new_cities(self, /, *identifiers) -> list[CityInfo]:
        """Create one or more cities ids and store in db"""

        result = []
        for idx in identifiers:
            city = CityInfo(api_id=idx)
            await self.insert(city)
            result.append(city)

        return result

    async def total_of_cities(self) -> int:
        """Total of cities in database"""

        return await self.database_manager.model_total_registries(CityInfo)


async def base_startup():
    redis = _redis_di_factory(_api_settings_builder())
    manager = AsyncDbManager(redis)
    repo = CityInfoRepository(manager)
    if await repo.total_of_cities() != 0:
        click.echo(f'Fixtures already loaded {click.style('...', fg="green")}')
        click.echo("Nothing to do!")

        return
    with open("config/city_list/sample.json") as f:
        click.echo(f"Loading fixture data {click.style('...', fg="green")}")
        data = json.load(f)
        click.echo(f"Saving data in database {click.style('...', fg="green")}")
        await repo.new_cities(*data)


CityInfoRepositoryDI = Annotated[
    CityInfoRepository, Depends(CityInfoRepository)
]
UserCityDataRepositoryDI = Annotated[
    UserCityDataRepository, Depends(UserCityDataRepository)
]
UserRepositoryDI = Annotated[UserRepository, Depends(UserRepository)]
