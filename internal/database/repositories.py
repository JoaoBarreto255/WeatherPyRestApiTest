"""Module for querie and save data"""

from typing import Type, Optional, Annotated

from fastapi import Depends
from sqlalchemy import select

from internal.database.manager import AsyncDbManagerDI, AsyncDbManager
from internal.database.schema import User, Data, AbstractAsyncEntity

class __BaseRepository:
    """ common repository logic """

    TYPE: Optional[Type[AbstractAsyncEntity]]  = None

    def __init__(self, manager: AsyncDbManagerDI) -> None:
        self.__database_manager = manager

    @property
    def database_manager(self) -> AsyncDbManager:
        return self.__database_manager
    
    async def find_by_id(self, id: int):
        assert self.TYPE is not None
        async with self.database_manager.async_session.begin() as conn:
            return await conn.execute(select(self.TYPE).where(self.TYPE.id == id).limit(1))
        
    async def create_entity(self, **kwargs):
        assert self.TYPE is not None
        classname = self.TYPE
        item = classname(**kwargs)

        async with self.database_manager.async_session.begin() as conn:
            async with conn.begin():
                conn.add(item)

class UserRepository(__BaseRepository):
    """
    User repository
    """
    TYPE = User

    async def new_user(self) -> User:
        return await self.create_entity()


UserRepositoryDI = Annotated[UserRepository, Depends(UserRepository)]
