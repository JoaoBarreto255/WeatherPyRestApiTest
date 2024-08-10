"""Api output models"""

import functools
import hashlib
import json
from datetime import datetime

from pydantic import BaseModel, Field

from internal.utils import build_singleton


@build_singleton
class ModelTableNameFactory:

    def __init__(self) -> None:
        pass

    def __call__(self, model) -> str:
        if not isinstance(model, type):
            model = type(model)

        return self.__digest_name(str(model))

    @functools.cache
    def __digest_name(self, name: str) -> str:
        hobj = hashlib.md5()
        hobj.update(name.encode())
        return hobj.hexdigest()


class Base(BaseModel):
    """Base from all models used by api"""

    index: int | None = Field(None, json_schema_extra={"minimum": 1})

    @classmethod
    def table_name(cls) -> str:
        factory = ModelTableNameFactory()
        return factory(cls)

    def db_index(self) -> str:
        return f'{self.table_name()}_{self.index or "0"}'


class User(Base):
    created_at: str = Field(min_length=10)
    requested_at: str | None = Field(None, min_length=1)
    processed_at: str | None = Field(None, min_length=1)
    processed: int = Field(0, json_schema_extra={"minimun": 0})


class UserCityData(Base):
    user_id: int = Field(json_schema_extra={"minimun": 1})
    request_time: str = Field(min_length=10)
    data: str = Field(min_length=2)

    @classmethod
    def build_from(cls, user_id: int, payload: dict):
        return cls(
            user_id=user_id,
            request_time=datetime.now().isoformat(),
            data=json.dumps(payload),
        )

    @property
    def payload(self) -> dict:
        return json.loads(self.data)


class CityInfo(Base):
    """Store info to retrieve api data"""

    api_id: int = Field(json_schema_extra={"minimun": 1})
