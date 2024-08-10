""" Manage and create users """

from fastapi.routing import APIRouter
from internal.database.repositories import UserRepositoryDI
from internal.settings import ApiSettingsDI
from internal.models import User

USERS_ROUTER = APIRouter()


@USERS_ROUTER.post("/users", status_code=201)
async def create_user(user_repo: UserRepositoryDI) -> User:
    return await user_repo.new_user()


@USERS_ROUTER.get("/users/{user_id}")
async def get_user(user_id: int, user_repo: UserRepositoryDI) -> User:
    return await user_repo.get_user(user_id)


@USERS_ROUTER.delete("/users/reset")
async def reset_users(
    user_repo: UserRepositoryDI, settings: ApiSettingsDI
) -> dict:
    if "dev" == settings.app_env:
        await user_repo.remove_all_users()

    return {"success": True}
