"""Api output models"""

import hashlib
import functools

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

    index: int | None = Field(None, gt=1)

    @classmethod
    def table_name(cls) -> str:
        factory = ModelTableNameFactory()
        return factory(cls)

    def db_index(self) -> str:
        return f'{self.table_name()}_{self.index or "0"}'


class User(Base):
    created_at: str
    requested_at: str | None = Field(None, min_length=1)
    processed_at: str | None = Field(None, min_length=1)
