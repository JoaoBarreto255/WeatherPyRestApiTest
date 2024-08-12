""" Main api entry point """

from fastapi import FastAPI
from api.routers.users import USERS_ROUTER
from api.routers.cities import CITIES_ROUTER


app = FastAPI()
app.include_router(USERS_ROUTER)
app.include_router(CITIES_ROUTER)

if __name__ == "__main__":
    print("Usage:")
    print(' uvicorn main:app [--reload "option in dev mode"]')
