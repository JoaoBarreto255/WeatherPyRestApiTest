"""Aplication settings"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import AmqpDsn, AnyUrl, Field, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    app_env: str = "dev"
    database_url: AnyUrl
    amqp_url: AmqpDsn = Field(alias="AMQP_DSN")
    queue_name: str = Field(min_length=1)

    @property
    def database_dsn(self) -> str:
        return str(self.database_url)

    @property
    def amqp_dsn(self) -> str:
        return str(self.amqp_url)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class ConsumerSettings(ApiSettings):
    weather_api_endpoint: AnyUrl
    weather_api_token: str = Field(min_length=1)
    redis_dsn: RedisDsn

    @property
    def weather_api_dsn(self) -> str:
        return str(self.weather_api_endpoint)


@lru_cache
def _api_settings_builder() -> ApiSettings:
    return ApiSettings()


ApiSettingsDI = Annotated[ApiSettings, Depends(_api_settings_builder)]


@lru_cache
def _consumer_settings_builder() -> ConsumerSettings:
    return ConsumerSettings()


ConsumerSettingsDI = Annotated[
    ConsumerSettings, Depends(_consumer_settings_builder)
]
