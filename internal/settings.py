"""Aplication settings"""

from pydantic_settings import BaseSettings


class ApiSettings(BaseSettings):
    app_env: str = "dev"
    database_url: str = ""
    rabbitmq_url: str = ""
    queue_name: str = ""


class ConsumerSettings(ApiSettings):
    weather_api_endpoint: str = ""
    weather_api_token: str = ""
