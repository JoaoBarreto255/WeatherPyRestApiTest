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
        """Create new user for download weather state"""
        user = User(created_at=datetime.now().isoformat())
        await self.database_manager.insert_registry(user)

        return user

    async def get_user(self, index: int) -> User:
        """Fecth user data"""
        return await self.database_manager.find_registry(User, index)

    async def remove_all_users(self) -> None:
        """Clear all users saved in database"""
        return await self.database_manager.clear_model_registries(User)


UserRepositoryDI = Annotated[UserRepository, Depends(UserRepository)]
