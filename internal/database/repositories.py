"""Module for querie and save data"""

from datetime import datetime
from typing import Annotated

from fastapi import Depends

from internal.database.manager import AsyncDbManagerDI, AsyncDbManager
from internal.models import User


class BaseRepository:
    """common repository logic"""

    def __init__(self, manager: AsyncDbManagerDI) -> None:
        self.database_manager = manager


class UserRepository(BaseRepository):
    """
    Api User repository
    """

    async def new_user(self) -> User:
        user = User(created_at=datetime.now().isoformat())
        await self.database_manager.insert_registry(user)

        return user


UserRepositoryDI = Annotated[UserRepository, Depends(UserRepository)]
