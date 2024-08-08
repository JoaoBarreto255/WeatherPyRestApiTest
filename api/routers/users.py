""" Manage and create users """

from fastapi.routing import APIRouter
from internal.database.repositories import UserRepositoryDI
from internal.models import UserOutput

USERS_ROUTER = APIRouter()


@USERS_ROUTER.post("/users", status_code=201)
async def create_user(user_repo: UserRepositoryDI) -> UserOutput:
    user = await user_repo.new_user()

    return UserOutput(user.id, user.created_at)


@USERS_ROUTER.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
