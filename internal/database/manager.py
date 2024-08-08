"""
Manager module - manage all app async operations.
"""

from typing import Union, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from internal.settings import ApiSettingsDI
from internal.database.schema import AbstractAsyncEntity, User, Data

class AsyncDbManager:
    """Assincronous database manage - Deal with all assincronous database operation"""

    __engine = None
    __session = None

    def __init__(self, settings: ApiSettingsDI) -> None:
        if self.__engine or self.__session:
            return

        self.__engine = create_async_engine(str(settings.database_url))
        self.__session = async_sessionmaker(self.__engine, expire_on_commit=False)

    async def bootstrap(self) -> None:
        async with self.__engine.begin() as conn:
            await conn.run_sync(AbstractAsyncEntity.metadata.create_all)

    @classmethod
    async def dispose(cls) -> None:
        cls.__session = None
        cls.__engine.dispose()
        cls.__engine = None

    @property
    def async_session(self):
        return self.__session
    

AsyncDbManagerDI = Annotated[AsyncDbManager, Depends(AsyncDbManager)]
    