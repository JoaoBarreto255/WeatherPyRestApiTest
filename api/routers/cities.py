""" Manage and create users """

from datetime import datetime

from fastapi import Response, status, HTTPException
from fastapi.routing import APIRouter

from internal.database.repositories import UserRepositoryDI
from internal.queue_manager import QueueManagerDI
from internal.models import UserCityData

CITIES_ROUTER = APIRouter()


@CITIES_ROUTER.post("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def request_start_process_cities(
    user_id: int, user_repo: UserRepositoryDI, queue_manager: QueueManagerDI
) -> None:
    """Start cities request for specified user."""
    user = await user_repo.get_user(user_id)
    user.requested_at = datetime.now().isoformat()
    await user_repo.update_user(user)
    await queue_manager.enqueue_user(user)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@CITIES_ROUTER.get("/{user_id}")
async def monitore_request_processed_percentage(
    user_id: int,
    user_repo: UserRepositoryDI,
) -> str:
    """Check user request process status."""

    USER = await user_repo.get_user(user_id)
    # TOTAL_OF_CITIES = await
    USER_PERCENTAGE = 10.0

    return f"{USER_PERCENTAGE:f.2}"


@CITIES_ROUTER.get("/{user_id}/result")
async def get_user_citie_request(
    user_id: int, user_repo: UserRepositoryDI
) -> list[UserCityData]:
    """Check user request process status."""

    USER = await user_repo.get_user(user_id)
    if USER.processed_at is None:
        raise HTTPException(status.HTTP_425_TOO_EARLY)

    return []
