""" Manage and create users """

from fastapi.routing import APIRouter

USERS_ROUTER = APIRouter()


@USERS_ROUTER.post("/users", status_code=201)
async def create_user():
    return {"user_id": 1}

@USERS_ROUTER.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
