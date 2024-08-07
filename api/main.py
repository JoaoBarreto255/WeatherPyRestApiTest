""" Main api entry point """

from contextlib import asynccontextmanager

from fastapi import FastAPI
from routers.users import USERS_ROUTER


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Start app batteries")
    yield
    print("Finish app batteries")


app = FastAPI()
app.include_router(USERS_ROUTER)

if __name__ == "__main__":
    print("Usage:")
    print(' uvicorn main:app [--reload "option in dev mode"]')
