""" Manage and create users """

from fastapi.routing import APIRouter
from internal.database.repositories import UserRepositoryDI
from internal.models import User

USERS_ROUTER = APIRouter()


@USERS_ROUTER.post("/users", status_code=201)
async def create_user(user_repo: UserRepositoryDI) -> User:
    return await user_repo.new_user()


@USERS_ROUTER.get("/users/{user_id}")
async def get_user(user_id: int, user_repo: UserRepositoryDI) -> User:
    return await user_repo.get_user(user_id)
