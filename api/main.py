""" Main api entry point """

from contextlib import asynccontextmanager

from fastapi import FastAPI
from api.routers.users import USERS_ROUTER
from internal.database.manager import AsyncDbManager
from internal.settings import _api_settings_builder

DATABASE_MANAGER = AsyncDbManager(_api_settings_builder())
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Start app batteries")
    await DATABASE_MANAGER.bootstrap()
    yield
    await DATABASE_MANAGER.dispose()
    print("Finish app batteries")


app = FastAPI(lifespan=lifespan)
app.include_router(USERS_ROUTER)

if __name__ == "__main__":
    print("Usage:")
    print(' uvicorn main:app [--reload "option in dev mode"]')
