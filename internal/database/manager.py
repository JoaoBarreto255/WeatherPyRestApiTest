"""
Manager module - manage all app async operations.
"""

from typing import Annotated, TypeVar

from fastapi import Depends, HTTPException
from redis import asyncio as async_redis

from internal.models import Base, User
from internal.utils import build_singleton, make_async_decorator
from internal.settings import ApiSettingsDI

TABLE_DATA_ITEM_TOTAL_KEY = "item_total"

M = TypeVar("M", Base, User)


def _redis_di_factory(settings: ApiSettingsDI) -> async_redis.Redis:
    return async_redis.from_url(settings.redis_dsn)


@build_singleton
class AsyncDbManager:
    """Assincronous database manage - Deal with all assincronous database operation"""

    def __init__(
        self, redis: Annotated[async_redis.Redis, Depends(_redis_di_factory)]
    ) -> None:
        self.redis = redis

    async def insert_registry(self, registry: Base) -> None:
        """Method insert_registry - create object in database"""
        registry.index = await self._pipeline_create_resgistry_index(registry)
        await self._pipeline_set_resgistry_fields(registry)

    async def update_registry(self, registry: Base) -> None:
        """Method update_registry - save object data in datababase"""
        if registry.index is None:
            raise HTTPException(400)

        await self._pipeline_set_resgistry_fields(registry)

    async def find_registry(self, model_class: M, idx: int) -> M:
        """
        Method find_registry - get item object from database
        """
        index = f"{model_class.table_name()}_{idx}"
        if not (result := await self.redis.hgetall(index)):
            raise HTTPException(404)

        result = {k.decode(): v.decode() for k, v in result.items()}

        return model_class(**result)

    async def _pipeline_set_resgistry_fields(self, registry: Base) -> None:
        """
        Method _pipeline_set_resgistry_fields - save entity registry data to redis
        """
        reg_index = registry.db_index()
        reg_dict = registry.model_dump()
        async with self.redis.pipeline() as pipe:
            await pipe.watch(reg_index)

            for key, value in reg_dict.items():
                if value is None:
                    continue

                await pipe.hset(reg_index, key, value)

            await pipe.unwatch()

    async def _pipeline_create_resgistry_index(self, registry: Base) -> int:
        """
        Method _pipeline_create_resgistry_index - Get new key for new item in database
        """
        table_data_key = f"table_data:{registry.table_name()}"
        async with self.redis.pipeline() as pipe:
            # lock key
            await pipe.watch(table_data_key)
            if (
                result := await pipe.hget(
                    table_data_key, TABLE_DATA_ITEM_TOTAL_KEY
                )
            ) is None:
                await pipe.hset(table_data_key, TABLE_DATA_ITEM_TOTAL_KEY, 1)
                await pipe.unwatch()

                return 1

            await pipe.hincrby(table_data_key, TABLE_DATA_ITEM_TOTAL_KEY)
            await pipe.unwatch()

            return int(result) + 1


AsyncDbManagerDI = Annotated[AsyncDbManager, Depends(AsyncDbManager)]
