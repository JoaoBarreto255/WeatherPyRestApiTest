"""
Services Module
Contain classes and function to execute some services.
"""

import asyncio
import json
from typing import Callable, Any

import aiohttp
from redis import asyncio as aioredis
from fastapi import status, HTTPException

from internal.database.manager import _redis_di_factory
from internal.settings import ConsumerSettings
from internal.utils import build_singleton


async def make_get_request(endpoint: str) -> dict[str, Any]:
    """Make get request to any service"""

    async with aiohttp.request("GET", endpoint) as response:
        if response.status != status.HTTP_200_OK:
            raise HTTPException(response.status)

        return await response.json()


@build_singleton
class RequestWeatherApiService:
    """Make requests from weather api service to obtain data"""

    def __init__(
        self,
        settings: ConsumerSettings,
        request_function: Callable[[str], dict] = make_get_request,
    ) -> None:
        self.api_dsn = settings.weather_api_dsn
        self.api_token = settings.weather_api_token
        self.request_function = request_function

    async def fetch_city(self, city_id: int) -> dict:
        """
        fetch weather data from city

        :param int city_id: External api id used to identifier city on their\
            base

        :raises fastapi.HTTPException: Any request with code different from **200 OK**.
        """

        endpoint = self.build_endpoint(city_id)

        return await self.request_function(endpoint, self.api_token)

    def build_endpoint(self, city_id: int) -> str:
        """
        Build url for made api request.

        :param int city_id: External api id used to identifier city on their\
            base

        url format: {api dsn}?id={city_id}&appid={api_key}
        """

        return f"{self.api_dsn}?id={city_id}&appid={self.api_token}"


def city_response_data_cleaner(data: dict) -> dict:
    """Cleans all unused city fetched data"""
    raise NotImplementedError


class CitiesFetchApiService:
    """
    **CitiesFetchApiService**: Help fetch all cities given.

    :param request_service: async service to request data from api.
    :param redis: async redis client for cache requested data.
    :param data_cleaner: function used to keep only used fields.
    :param hold_time: time in seconds to wait next request. (default 300s)
    """

    def __init__(
        self,
        request_service: RequestWeatherApiService,
        redis: aioredis.Redis,
        data_cleaner: Callable[[dict], dict] = city_response_data_cleaner,
        hold_time: int = 1,
    ) -> None:
        """
        :param request_service: async service to request data from api.
        :param redis: async redis client for cache requested data.
        :param data_cleaner: function used to keep only used fields.
        :param hold_time: time in seconds to wait next request. (default 1s)  
        """

        self.request_service = request_service
        self.redis = redis
        self.data_cleaner = data_cleaner
        self.hold_time = hold_time

    async def fetch_all_list_cities(self, cities_list: list[int]):
        """
        Iterates over list cities and get all data of each city and yield\
            it await time for next request

        usage:
        ```python

        service = CitiesFetchApiService(...)
        async for city_data in service.fetch_all_list_cities([1,2,3]):
            # do you stuff
            pass
        ```

        :param list[int] cities_list: list of ids for fetch in api

        :raises HTTPException: everytime that a city request code is not **200 OK**
        """

        for city_id in cities_list:
            yield await self.fetch_city(city_id)

    async def fetch_city(self, city_id: int) -> dict:
        """
        fetch weather data from city if not found it in cache

        :param int city_id: External api id used to identifier city on their\
            base

        :raises fastapi.HTTPException: Any request with code different from **200 OK**.
        """

        CITY_CACHE_KEY = f"city:cache:{city_id}"

        if json_str := await self.redis.getex(CITY_CACHE_KEY):
            return json.loads(json_str)
        
        weather_data = await self.request_service.fetch_city(city_id)
        weather_data = self.data_cleaner(weather_data)
        await self.redis.setex(CITY_CACHE_KEY, 300, json.dumps(weather_data)) 
        await asyncio.sleep(self.hold_time)

        return weather_data
