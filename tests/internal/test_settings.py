import pytest

from internal.settings import ApiSettings, ConsumerSettings

TEST_REDIS_DSN = "redis://localhost:6379/1"
TEST_AMQP_DSN = "amqp://user:pass@localhost:5672/"
TEST_QUEUE_NAME = "foo"
TEST_WEATHER_API_ENDPOINT = "https://foo.com/"
TEST_WEATHER_API_TOKEN = "bar"


def api_settings_factory() -> ApiSettings:
    return ApiSettings(
        REDIS_DSN=TEST_REDIS_DSN,
        AMQP_DSN=TEST_AMQP_DSN,
        queue_name=TEST_QUEUE_NAME,
    )


def consumer_settings_factory() -> ConsumerSettings:
    return ConsumerSettings(
        REDIS_DSN=TEST_REDIS_DSN,
        AMQP_DSN=TEST_AMQP_DSN,
        queue_name=TEST_QUEUE_NAME,
        weather_api_endpoint=TEST_WEATHER_API_ENDPOINT,
        weather_api_token=TEST_WEATHER_API_TOKEN,
    )


def test_api_settings_redis_dsn_property() -> None:
    assert api_settings_factory().redis_dsn == TEST_REDIS_DSN


def test_api_settings_ampq_dsn_property() -> None:
    assert api_settings_factory().amqp_dsn == TEST_AMQP_DSN


def test_consumer_settings_weather_api_dsn() -> None:
    assert (
        consumer_settings_factory().weather_api_dsn
        == TEST_WEATHER_API_ENDPOINT
    )
