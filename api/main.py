""" Main api entry point """

from fastapi import FastAPI
from api.routers.users import USERS_ROUTER


app = FastAPI()
app.include_router(USERS_ROUTER)

if __name__ == "__main__":
    print("Usage:")
    print(' uvicorn main:app [--reload "option in dev mode"]')
