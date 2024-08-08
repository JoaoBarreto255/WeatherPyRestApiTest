"""
Manager module - manage all app async operations.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from internal.settings import ApiSettingsDI
from internal.database.schema import AbstractAsyncEntity, User, Data

class AsyncDbManager:
    """Assincronous database manage - Deal with all assincronous database operation"""

    def __init__(self, settings: ApiSettingsDI) -> None:
        self.__engine = create_async_engine(str(settings.database_url))
        self.__session = async_sessionmaker(self.__engine, expire_on_commit=False)

    async def bootstrap(self) -> None:
        async with self.__engine.begin() as conn:
            await conn.run_sync(AbstractAsyncEntity.metadata.create_all)

    async def dispose(self) -> None:
        await self.__engine.dispose()

    @property
    def async_session(self):
        return self.__session


__ASYNC_DB_MANAGER_INSTANCE = None

def async_db_manager_factory(settings: ApiSettingsDI) -> AsyncDbManager:
    global __ASYNC_DB_MANAGER_INSTANCE
    if __ASYNC_DB_MANAGER_INSTANCE is None:
        __ASYNC_DB_MANAGER_INSTANCE = AsyncDbManager(settings) 

    return __ASYNC_DB_MANAGER_INSTANCE


AsyncDbManagerDI = Annotated[AsyncDbManager, Depends(async_db_manager_factory)]
    