"""Aplication settings"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import AmqpDsn, AnyUrl, Field, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    app_env: str = "dev"
    redis_url: RedisDsn = Field(alias="REDIS_DSN")
    amqp_url: AmqpDsn = Field(alias="AMQP_DSN")
    queue_name: str = Field(min_length=1)

    @property
    def redis_dsn(self) -> str:
        dsn = self.redis_url
        return f"{dsn.scheme}://{dsn.host}:{dsn.port}{dsn.path}"

    @property
    def amqp_dsn(self) -> str:
        return str(self.amqp_url)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class ConsumerSettings(ApiSettings):
    weather_api_endpoint: AnyUrl
    weather_api_token: str = Field(min_length=1)

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
